import os
import json
import shutil
import tarfile
import datetime
import logging
from pathlib import Path
import sqlite3

class BackupManager:
    def __init__(self):
        self.config_dir = Path("/opt/sshplus/config")
        self.backup_dir = Path("/opt/sshplus/backups")
        self.db_file = Path("/opt/sshplus/database/users.db")
        self.setup()
    
    def setup(self):
        """Initialize backup directory"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
    
    def create_backup(self, backup_name=None):
        """Create a backup of all system configurations and user data"""
        try:
            # Generate backup name if not provided
            if not backup_name:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"sshplus_backup_{timestamp}"
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Backup configuration files
            self._backup_configs(backup_path)
            
            # Backup database
            self._backup_database(backup_path)
            
            # Backup V2Ray configurations
            self._backup_v2ray(backup_path)
            
            # Create tarball
            tar_path = f"{backup_path}.tar.gz"
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(backup_path, arcname=backup_name)
            
            # Remove temporary backup directory
            shutil.rmtree(backup_path)
            
            return True, {
                "backup_file": tar_path,
                "timestamp": timestamp,
                "size": os.path.getsize(tar_path)
            }
        except Exception as e:
            logging.error(f"Error creating backup: {str(e)}")
            return False, f"Error creating backup: {str(e)}"
    
    def restore_backup(self, backup_file):
        """Restore system from a backup file"""
        try:
            # Extract backup
            with tarfile.open(backup_file, "r:gz") as tar:
                backup_name = tar.getnames()[0]
                tar.extractall(self.backup_dir)
            
            backup_path = self.backup_dir / backup_name
            
            # Stop services
            os.system("systemctl stop sshplus")
            os.system("systemctl stop v2ray")
            
            # Restore configurations
            self._restore_configs(backup_path)
            
            # Restore database
            self._restore_database(backup_path)
            
            # Restore V2Ray configurations
            self._restore_v2ray(backup_path)
            
            # Restart services
            os.system("systemctl start v2ray")
            os.system("systemctl start sshplus")
            
            # Clean up
            shutil.rmtree(backup_path)
            
            return True, "Backup restored successfully"
        except Exception as e:
            logging.error(f"Error restoring backup: {str(e)}")
            return False, f"Error restoring backup: {str(e)}"
    
    def list_backups(self):
        """List all available backups"""
        try:
            backups = []
            for backup in self.backup_dir.glob("*.tar.gz"):
                backups.append({
                    "name": backup.stem,
                    "path": str(backup),
                    "size": os.path.getsize(backup),
                    "created": datetime.datetime.fromtimestamp(os.path.getctime(backup))
                })
            return True, backups
        except Exception as e:
            logging.error(f"Error listing backups: {str(e)}")
            return False, f"Error listing backups: {str(e)}"
    
    def delete_backup(self, backup_name):
        """Delete a backup file"""
        try:
            backup_file = self.backup_dir / f"{backup_name}.tar.gz"
            if backup_file.exists():
                backup_file.unlink()
                return True, f"Backup {backup_name} deleted successfully"
            else:
                return False, f"Backup {backup_name} not found"
        except Exception as e:
            logging.error(f"Error deleting backup: {str(e)}")
            return False, f"Error deleting backup: {str(e)}"
    
    def _backup_configs(self, backup_path):
        """Backup configuration files"""
        config_backup = backup_path / "config"
        config_backup.mkdir(exist_ok=True)
        
        # Copy all configuration files
        for config_file in self.config_dir.glob("*.json"):
            shutil.copy2(config_file, config_backup)
    
    def _backup_database(self, backup_path):
        """Backup SQLite database"""
        if self.db_file.exists():
            # Create a database backup
            db_backup = backup_path / "database"
            db_backup.mkdir(exist_ok=True)
            
            conn = sqlite3.connect(self.db_file)
            with open(db_backup / "users.sql", 'w') as f:
                for line in conn.iterdump():
                    f.write(f"{line}\n")
            conn.close()
    
    def _backup_v2ray(self, backup_path):
        """Backup V2Ray configurations"""
        v2ray_config = Path("/usr/local/etc/v2ray/config.json")
        if v2ray_config.exists():
            v2ray_backup = backup_path / "v2ray"
            v2ray_backup.mkdir(exist_ok=True)
            shutil.copy2(v2ray_config, v2ray_backup)
    
    def _restore_configs(self, backup_path):
        """Restore configuration files"""
        config_backup = backup_path / "config"
        if config_backup.exists():
            for config_file in config_backup.glob("*.json"):
                shutil.copy2(config_file, self.config_dir)
    
    def _restore_database(self, backup_path):
        """Restore SQLite database"""
        db_backup = backup_path / "database" / "users.sql"
        if db_backup.exists():
            # Create new database
            if self.db_file.exists():
                self.db_file.unlink()
            
            conn = sqlite3.connect(self.db_file)
            with open(db_backup) as f:
                conn.executescript(f.read())
            conn.close()
    
    def _restore_v2ray(self, backup_path):
        """Restore V2Ray configurations"""
        v2ray_backup = backup_path / "v2ray" / "config.json"
        if v2ray_backup.exists():
            shutil.copy2(v2ray_backup, "/usr/local/etc/v2ray/config.json") 