import os
import json
import logging
from pathlib import Path
import subprocess

class BannerManager:
    def __init__(self):
        self.config_dir = Path("/opt/sshplus/config")
        self.banner_file = Path("/etc/ssh/banner")
        self.motd_file = Path("/etc/motd")
        self.banner_config_file = self.config_dir / "banner_config.json"
        self.setup()
    
    def setup(self):
        """Initialize banner configuration"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
        
        if not self.banner_config_file.exists():
            default_config = {
                "enabled": True,
                "show_system_info": True,
                "show_user_info": True,
                "custom_message": "Welcome to SSHPlus Pro",
                "banner_style": "default"
            }
            with open(self.banner_config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
    
    def set_banner(self, message=None, style=None):
        """Set SSH banner with custom message and style"""
        try:
            config = self.load_config()
            
            if message:
                config["custom_message"] = message
            if style:
                config["banner_style"] = style
            
            self.save_config(config)
            
            # Generate banner content
            banner_content = self._generate_banner(config)
            
            # Save banner
            with open(self.banner_file, 'w') as f:
                f.write(banner_content)
            
            # Update SSH config to use banner
            self._update_ssh_config()
            
            return True, "Banner updated successfully"
        except Exception as e:
            logging.error(f"Error setting banner: {str(e)}")
            return False, f"Error setting banner: {str(e)}"
    
    def set_motd(self, message=None):
        """Set Message of the Day"""
        try:
            config = self.load_config()
            
            if message:
                config["motd_message"] = message
            
            self.save_config(config)
            
            # Generate MOTD content
            motd_content = self._generate_motd(config)
            
            # Save MOTD
            with open(self.motd_file, 'w') as f:
                f.write(motd_content)
            
            return True, "MOTD updated successfully"
        except Exception as e:
            logging.error(f"Error setting MOTD: {str(e)}")
            return False, f"Error setting MOTD: {str(e)}"
    
    def toggle_system_info(self, enabled=True):
        """Toggle system information display in banner"""
        try:
            config = self.load_config()
            config["show_system_info"] = enabled
            self.save_config(config)
            
            # Update banner
            self.set_banner()
            
            return True, f"System info display {'enabled' if enabled else 'disabled'}"
        except Exception as e:
            logging.error(f"Error toggling system info: {str(e)}")
            return False, f"Error toggling system info: {str(e)}"
    
    def toggle_user_info(self, enabled=True):
        """Toggle user information display in banner"""
        try:
            config = self.load_config()
            config["show_user_info"] = enabled
            self.save_config(config)
            
            # Update banner
            self.set_banner()
            
            return True, f"User info display {'enabled' if enabled else 'disabled'}"
        except Exception as e:
            logging.error(f"Error toggling user info: {str(e)}")
            return False, f"Error toggling user info: {str(e)}"
    
    def _generate_banner(self, config):
        """Generate banner content based on configuration"""
        banner = []
        
        # Add styled header based on selected style
        if config["banner_style"] == "default":
            banner.extend([
                "================================",
                "       SSHPlus Pro Server       ",
                "================================"
            ])
        elif config["banner_style"] == "ascii":
            banner.extend([
                " ____  ____  _   _ ____  _     _   _ ____  ",
                "/ ___|| __ )| | | |  _ \\| |   | | | / ___| ",
                "\\___ \\|  _ \\| |_| | |_) | |   | | | \\___ \\ ",
                " ___) | |_) |  _  |  __/| |___| |_| |___) |",
                "|____/|____/|_| |_|_|   |_____|\\___/|____/ "
            ])
        
        # Add custom message
        banner.extend(["", config["custom_message"], ""])
        
        # Add system information if enabled
        if config["show_system_info"]:
            system_info = self._get_system_info()
            banner.extend([
                "System Information:",
                f"OS: {system_info['os']}",
                f"Kernel: {system_info['kernel']}",
                f"CPU Usage: {system_info['cpu_usage']}%",
                f"Memory Usage: {system_info['memory_usage']}%",
                f"Uptime: {system_info['uptime']}"
            ])
        
        # Add user information if enabled
        if config["show_user_info"]:
            user_info = self._get_user_info()
            banner.extend([
                "",
                "Connection Information:",
                f"Total Users: {user_info['total_users']}",
                f"Active Connections: {user_info['active_connections']}",
                f"Server Load: {user_info['server_load']}"
            ])
        
        return "\n".join(banner)
    
    def _generate_motd(self, config):
        """Generate MOTD content based on configuration"""
        motd = []
        
        if "motd_message" in config:
            motd.append(config["motd_message"])
        
        motd.extend([
            "",
            "Type 'menu' to access SSHPlus Pro management interface",
            "Type 'help' for available commands"
        ])
        
        return "\n".join(motd)
    
    def _get_system_info(self):
        """Get system information"""
        try:
            # Get OS information
            os_info = subprocess.check_output("cat /etc/os-release | grep PRETTY_NAME", shell=True).decode()
            os_name = os_info.split("=")[1].strip().strip('"')
            
            # Get kernel version
            kernel = subprocess.check_output("uname -r", shell=True).decode().strip()
            
            # Get CPU usage
            cpu_usage = subprocess.check_output("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", shell=True).decode().strip()
            
            # Get memory usage
            memory = subprocess.check_output("free | grep Mem | awk '{print ($3/$2) * 100}'", shell=True).decode().strip()
            
            # Get uptime
            uptime = subprocess.check_output("uptime -p", shell=True).decode().strip()
            
            return {
                "os": os_name,
                "kernel": kernel,
                "cpu_usage": float(cpu_usage),
                "memory_usage": float(memory),
                "uptime": uptime
            }
        except:
            return {
                "os": "Unknown",
                "kernel": "Unknown",
                "cpu_usage": 0,
                "memory_usage": 0,
                "uptime": "Unknown"
            }
    
    def _get_user_info(self):
        """Get user and connection information"""
        try:
            # Get total users
            total_users = len(subprocess.check_output("cat /etc/passwd | grep /home/", shell=True).decode().splitlines())
            
            # Get active connections
            active_connections = len(subprocess.check_output("netstat -tn | grep ESTABLISHED", shell=True).decode().splitlines())
            
            # Get server load
            load = subprocess.check_output("uptime | awk -F'load average:' '{ print $2 }'", shell=True).decode().strip()
            
            return {
                "total_users": total_users,
                "active_connections": active_connections,
                "server_load": load
            }
        except:
            return {
                "total_users": 0,
                "active_connections": 0,
                "server_load": "0.00, 0.00, 0.00"
            }
    
    def _update_ssh_config(self):
        """Update SSH configuration to use banner"""
        try:
            ssh_config = Path("/etc/ssh/sshd_config")
            
            # Read current config
            with open(ssh_config, 'r') as f:
                config_lines = f.readlines()
            
            # Update or add Banner line
            banner_line = f"Banner {self.banner_file}\n"
            banner_found = False
            
            for i, line in enumerate(config_lines):
                if line.startswith("Banner "):
                    config_lines[i] = banner_line
                    banner_found = True
                    break
            
            if not banner_found:
                config_lines.append(banner_line)
            
            # Write updated config
            with open(ssh_config, 'w') as f:
                f.writelines(config_lines)
            
            # Restart SSH service
            os.system("systemctl restart sshd")
            
            return True
        except Exception as e:
            logging.error(f"Error updating SSH config: {str(e)}")
            return False
    
    def load_config(self):
        """Load banner configuration"""
        with open(self.banner_config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self, config):
        """Save banner configuration"""
        with open(self.banner_config_file, 'w') as f:
            json.dump(config, f, indent=4) 