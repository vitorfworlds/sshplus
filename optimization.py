import os
import subprocess
import json
import speedtest
import logging
from pathlib import Path

class NetworkOptimizer:
    def __init__(self):
        self.config_dir = Path("/opt/sshplus/config")
        self.config_file = self.config_dir / "network_config.json"
        self.badvpn_port = 7300
        self.setup()
        
    def setup(self):
        """Initialize configuration and create necessary directories"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
        
        if not self.config_file.exists():
            default_config = {
                "badvpn_enabled": False,
                "tcp_tweaks_enabled": False,
                "badvpn_ports": [7300],
                "tcp_tweaks": {
                    "tcp_window_scaling": 1,
                    "tcp_congestion_control": "bbr",
                    "tcp_slow_start_after_idle": 0
                }
            }
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
    
    def install_badvpn(self):
        """Install and configure BadVPN"""
        try:
            # Download and compile BadVPN
            os.system("wget https://github.com/ambrop72/badvpn/archive/refs/tags/1.999.130.tar.gz")
            os.system("tar xf 1.999.130.tar.gz")
            os.chdir("badvpn-1.999.130")
            os.system("cmake -DBUILD_NOTHING_BY_DEFAULT=1 -DBUILD_UDPGW=1")
            os.system("make install")
            
            # Create systemd service
            service_content = """[Unit]
Description=BadVPN UDPGW Service
After=network.target

[Service]
ExecStart=/usr/local/bin/badvpn-udpgw --listen-addr 127.0.0.1:7300 --max-clients 1000 --max-connections-for-client 10
Restart=always

[Install]
WantedBy=multi-user.target"""
            
            with open("/etc/systemd/system/badvpn.service", "w") as f:
                f.write(service_content)
            
            os.system("systemctl daemon-reload")
            os.system("systemctl enable badvpn")
            os.system("systemctl start badvpn")
            
            # Update config
            config = self.load_config()
            config["badvpn_enabled"] = True
            self.save_config(config)
            
            return True, "BadVPN installed and configured successfully"
        except Exception as e:
            logging.error(f"Error installing BadVPN: {str(e)}")
            return False, f"Error installing BadVPN: {str(e)}"
    
    def install_tcp_tweaker(self):
        """Install and configure TCP Tweaker"""
        try:
            # Backup original sysctl.conf
            os.system("cp /etc/sysctl.conf /etc/sysctl.conf.backup")
            
            # Apply TCP optimizations
            tweaks = """
# TCP Tweaks
net.ipv4.tcp_window_scaling = 1
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 16384 16777216
net.ipv4.tcp_low_latency = 1
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.tcp_congestion_control = bbr"""
            
            with open("/etc/sysctl.conf", "a") as f:
                f.write(tweaks)
            
            os.system("sysctl -p")
            
            # Update config
            config = self.load_config()
            config["tcp_tweaks_enabled"] = True
            self.save_config(config)
            
            return True, "TCP Tweaker installed and configured successfully"
        except Exception as e:
            logging.error(f"Error installing TCP Tweaker: {str(e)}")
            return False, f"Error installing TCP Tweaker: {str(e)}"
    
    def run_speedtest(self):
        """Run speedtest and return results"""
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            
            # Run tests
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            ping = st.results.ping
            
            result = {
                "download": round(download_speed, 2),
                "upload": round(upload_speed, 2),
                "ping": round(ping, 2),
                "server": st.results.server["sponsor"]
            }
            
            return True, result
        except Exception as e:
            logging.error(f"Error running speedtest: {str(e)}")
            return False, f"Error running speedtest: {str(e)}"
    
    def set_user_speed_limit(self, username, download_limit=None, upload_limit=None):
        """Set speed limits for a specific user using tc"""
        try:
            # Get user's processes
            processes = subprocess.check_output(f"ps -u {username}", shell=True).decode()
            
            if download_limit:
                # Apply download limit
                os.system(f"tc qdisc add dev eth0 root handle 1: htb default 10")
                os.system(f"tc class add dev eth0 parent 1: classid 1:1 htb rate {download_limit}mbit")
                os.system(f"tc filter add dev eth0 protocol ip parent 1: prio 1 u32 match ip dst {username} flowid 1:1")
            
            if upload_limit:
                # Apply upload limit
                os.system(f"tc qdisc add dev eth0 root handle 1: htb default 10")
                os.system(f"tc class add dev eth0 parent 1: classid 1:2 htb rate {upload_limit}mbit")
                os.system(f"tc filter add dev eth0 protocol ip parent 1: prio 1 u32 match ip src {username} flowid 1:2")
            
            return True, f"Speed limits set for user {username}"
        except Exception as e:
            logging.error(f"Error setting speed limit: {str(e)}")
            return False, f"Error setting speed limit: {str(e)}"
    
    def remove_user_speed_limit(self, username):
        """Remove speed limits for a specific user"""
        try:
            os.system(f"tc qdisc del dev eth0 root")
            return True, f"Speed limits removed for user {username}"
        except Exception as e:
            logging.error(f"Error removing speed limit: {str(e)}")
            return False, f"Error removing speed limit: {str(e)}"
    
    def load_config(self):
        """Load network configuration"""
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self, config):
        """Save network configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4) 