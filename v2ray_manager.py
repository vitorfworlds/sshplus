import os
import json
import uuid
import base64
import logging
from pathlib import Path
import subprocess

class V2RayManager:
    def __init__(self):
        self.config_dir = Path("/opt/sshplus/config")
        self.v2ray_config_file = self.config_dir / "v2ray_config.json"
        self.v2ray_users_file = self.config_dir / "v2ray_users.json"
        self.setup()
    
    def setup(self):
        """Initialize configuration and create necessary directories"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
        
        if not self.v2ray_config_file.exists():
            default_config = {
                "enabled": False,
                "port": 10086,
                "protocol": "vmess",
                "network": "ws",
                "security": "auto",
                "ws_path": "/v2ray"
            }
            with open(self.v2ray_config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
        
        if not self.v2ray_users_file.exists():
            with open(self.v2ray_users_file, 'w') as f:
                json.dump([], f, indent=4)
    
    def install_v2ray(self):
        """Install V2Ray"""
        try:
            # Download V2Ray install script
            os.system("curl -O https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh")
            os.system("chmod +x install-release.sh")
            os.system("./install-release.sh")
            
            # Create basic configuration
            config = {
                "inbounds": [{
                    "port": 10086,
                    "protocol": "vmess",
                    "settings": {
                        "clients": []
                    },
                    "streamSettings": {
                        "network": "ws",
                        "wsSettings": {
                            "path": "/v2ray"
                        }
                    }
                }],
                "outbounds": [{
                    "protocol": "freedom",
                    "settings": {}
                }]
            }
            
            with open("/usr/local/etc/v2ray/config.json", 'w') as f:
                json.dump(config, f, indent=4)
            
            # Start and enable V2Ray service
            os.system("systemctl enable v2ray")
            os.system("systemctl start v2ray")
            
            # Update config
            v2ray_config = self.load_config()
            v2ray_config["enabled"] = True
            self.save_config(v2ray_config)
            
            return True, "V2Ray installed and configured successfully"
        except Exception as e:
            logging.error(f"Error installing V2Ray: {str(e)}")
            return False, f"Error installing V2Ray: {str(e)}"
    
    def add_user(self, username, email=None, alter_id=0):
        """Add a new V2Ray user"""
        try:
            users = self.load_users()
            
            # Generate UUID
            user_id = str(uuid.uuid4())
            
            new_user = {
                "username": username,
                "email": email or f"{username}@v2ray.com",
                "id": user_id,
                "alter_id": alter_id,
                "enabled": True
            }
            
            users.append(new_user)
            self.save_users(users)
            
            # Update V2Ray config
            self._update_v2ray_config()
            
            # Generate client config
            client_config = self._generate_client_config(new_user)
            
            return True, {
                "user": new_user,
                "client_config": client_config,
                "vmess_url": self._generate_vmess_url(new_user)
            }
        except Exception as e:
            logging.error(f"Error adding V2Ray user: {str(e)}")
            return False, f"Error adding V2Ray user: {str(e)}"
    
    def remove_user(self, username):
        """Remove a V2Ray user"""
        try:
            users = self.load_users()
            users = [u for u in users if u["username"] != username]
            self.save_users(users)
            
            # Update V2Ray config
            self._update_v2ray_config()
            
            return True, f"User {username} removed successfully"
        except Exception as e:
            logging.error(f"Error removing V2Ray user: {str(e)}")
            return False, f"Error removing V2Ray user: {str(e)}"
    
    def list_users(self):
        """List all V2Ray users"""
        try:
            users = self.load_users()
            return True, users
        except Exception as e:
            logging.error(f"Error listing V2Ray users: {str(e)}")
            return False, f"Error listing V2Ray users: {str(e)}"
    
    def _update_v2ray_config(self):
        """Update V2Ray configuration with current users"""
        try:
            users = self.load_users()
            config = self.load_config()
            
            v2ray_config = {
                "inbounds": [{
                    "port": config["port"],
                    "protocol": config["protocol"],
                    "settings": {
                        "clients": [
                            {
                                "id": user["id"],
                                "alterId": user["alter_id"],
                                "email": user["email"]
                            }
                            for user in users if user["enabled"]
                        ]
                    },
                    "streamSettings": {
                        "network": config["network"],
                        "wsSettings": {
                            "path": config["ws_path"]
                        }
                    }
                }],
                "outbounds": [{
                    "protocol": "freedom",
                    "settings": {}
                }]
            }
            
            with open("/usr/local/etc/v2ray/config.json", 'w') as f:
                json.dump(v2ray_config, f, indent=4)
            
            # Restart V2Ray service
            os.system("systemctl restart v2ray")
            
            return True
        except Exception as e:
            logging.error(f"Error updating V2Ray config: {str(e)}")
            return False
    
    def _generate_client_config(self, user):
        """Generate client configuration for a user"""
        config = self.load_config()
        
        return {
            "v": "2",
            "ps": user["username"],
            "add": self._get_server_ip(),
            "port": str(config["port"]),
            "id": user["id"],
            "aid": str(user["alter_id"]),
            "net": config["network"],
            "type": "none",
            "host": "",
            "path": config["ws_path"],
            "tls": ""
        }
    
    def _generate_vmess_url(self, user):
        """Generate VMess URL for a user"""
        client_config = self._generate_client_config(user)
        config_str = json.dumps(client_config)
        return f"vmess://{base64.b64encode(config_str.encode()).decode()}"
    
    def _get_server_ip(self):
        """Get server's public IP address"""
        try:
            return subprocess.check_output("curl -s ifconfig.me", shell=True).decode().strip()
        except:
            return "YOUR_SERVER_IP"
    
    def load_config(self):
        """Load V2Ray configuration"""
        with open(self.v2ray_config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self, config):
        """Save V2Ray configuration"""
        with open(self.v2ray_config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def load_users(self):
        """Load V2Ray users"""
        with open(self.v2ray_users_file, 'r') as f:
            return json.load(f)
    
    def save_users(self, users):
        """Save V2Ray users"""
        with open(self.v2ray_users_file, 'w') as f:
            json.dump(users, f, indent=4) 