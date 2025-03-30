#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Function to print status messages
print_status() {
    echo -e "${YELLOW}[*] $1${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}[+] $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}[-] $1${NC}"
}

# Update system
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
print_status "Installing dependencies..."
apt-get install -y python3 python3-pip sqlite3 openssh-server squid iptables \
    net-tools wget curl tar zip unzip cmake build-essential speedtest-cli \
    netfilter-persistent iptables-persistent

# Create directory structure
print_status "Creating directory structure..."
mkdir -p /opt/sshplus/{config,database,logs,backups}
chmod 755 /opt/sshplus
chmod 700 /opt/sshplus/{config,database,logs,backups}

# Install Python dependencies
print_status "Installing Python dependencies..."
cat > /opt/sshplus/requirements.txt << EOF
speedtest-cli>=2.1.3
python-telegram-bot>=13.7
psutil>=5.8.0
requests>=2.26.0
cryptography>=3.4.7
EOF

pip3 install -r /opt/sshplus/requirements.txt

# Install BadVPN
print_status "Installing BadVPN..."
cd /tmp
wget https://github.com/ambrop72/badvpn/archive/refs/tags/1.999.130.tar.gz
tar xf 1.999.130.tar.gz
cd badvpn-1.999.130
cmake -DBUILD_NOTHING_BY_DEFAULT=1 -DBUILD_UDPGW=1
make install
cd ..
rm -rf badvpn-1.999.130 1.999.130.tar.gz

# Create BadVPN service
cat > /etc/systemd/system/badvpn.service << EOF
[Unit]
Description=BadVPN UDPGW Service
After=network.target

[Service]
ExecStart=/usr/local/bin/badvpn-udpgw --listen-addr 127.0.0.1:7300 --max-clients 1000 --max-connections-for-client 10
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable badvpn
systemctl start badvpn

# Install V2Ray
print_status "Installing V2Ray..."
curl -O https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh
chmod +x install-release.sh
./install-release.sh
rm install-release.sh

# Configure V2Ray
cat > /usr/local/etc/v2ray/config.json << EOF
{
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
EOF

systemctl enable v2ray
systemctl start v2ray

# Configure Squid Proxy
print_status "Configuring Squid Proxy..."
mv /etc/squid/squid.conf /etc/squid/squid.conf.bak
cat > /etc/squid/squid.conf << EOF
http_port 3128
http_port 8080
http_port 8799
http_port 3128
visible_hostname SSHPlus

acl localhost src 127.0.0.1/32 ::1
acl to_localhost dst 127.0.0.0/8 0.0.0.0/32 ::1
acl SSL_ports port 443
acl Safe_ports port 80
acl Safe_ports port 21
acl Safe_ports port 443
acl Safe_ports port 70
acl Safe_ports port 210
acl Safe_ports port 1025-65535
acl Safe_ports port 280
acl Safe_ports port 488
acl Safe_ports port 591
acl Safe_ports port 777
acl CONNECT method CONNECT

http_access allow localhost
http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports
http_access allow all

coredump_dir /var/spool/squid
refresh_pattern ^ftp: 1440 20% 10080
refresh_pattern ^gopher: 1440 0% 1440
refresh_pattern -i (/cgi-bin/|\?) 0 0% 0
refresh_pattern . 0 20% 4320
EOF

systemctl enable squid
systemctl restart squid

# Configure SSH
print_status "Configuring SSH..."
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
cat > /etc/ssh/sshd_config << EOF
Port 22
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_dsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
UsePrivilegeSeparation yes
KeyRegenerationInterval 3600
ServerKeyBits 1024
SyslogFacility AUTH
LogLevel INFO
LoginGraceTime 120
PermitRootLogin yes
StrictModes yes
RSAAuthentication yes
PubkeyAuthentication yes
IgnoreRhosts yes
RhostsRSAAuthentication no
HostbasedAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
PasswordAuthentication yes
X11Forwarding yes
X11DisplayOffset 10
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server
UsePAM yes
Banner /etc/ssh/banner
EOF

# Create banner
cat > /etc/ssh/banner << EOF
================================
       SSHPlus Pro Server       
================================

Welcome to SSHPlus Pro!
Type 'menu' to access the management interface.
EOF

systemctl restart ssh

# Configure firewall
print_status "Configuring firewall..."
# Backup iptables rules
iptables-save > /opt/sshplus/config/iptables.backup

# Clear existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

# Set default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow Squid Proxy ports
iptables -A INPUT -p tcp --dport 3128 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
iptables -A INPUT -p tcp --dport 8799 -j ACCEPT

# Allow V2Ray
iptables -A INPUT -p tcp --dport 10086 -j ACCEPT

# Allow BadVPN
iptables -A INPUT -p udp --dport 7300 -j ACCEPT

# Save rules
netfilter-persistent save

# Create SSHPlus service
print_status "Creating SSHPlus service..."
cat > /etc/systemd/system/sshplus.service << EOF
[Unit]
Description=SSHPlus Pro Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/sshplus
ExecStart=/usr/bin/python3 /opt/sshplus/menu.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable sshplus
systemctl start sshplus

# Create menu command
print_status "Creating menu command..."
cat > /usr/bin/menu << EOF
#!/bin/bash
python3 /opt/sshplus/menu.py
EOF

chmod +x /usr/bin/menu

# Apply TCP optimizations
print_status "Applying TCP optimizations..."
cp /etc/sysctl.conf /etc/sysctl.conf.bak
cat >> /etc/sysctl.conf << EOF

# TCP Tweaks
net.ipv4.tcp_window_scaling = 1
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 16384 16777216
net.ipv4.tcp_low_latency = 1
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.tcp_congestion_control = bbr
EOF

sysctl -p

# Final cleanup
print_status "Cleaning up..."
apt-get clean
apt-get autoremove -y

print_success "Installation completed successfully!"
echo
echo "SSHPlus Pro has been installed and configured."
echo "Type 'menu' to access the management interface."
echo
echo "Default ports:"
echo "SSH: 22"
echo "Proxy: 3128, 8080, 8799"
echo "V2Ray: 10086"
echo "BadVPN: 7300"
echo
echo "Remember to:"
echo "1. Configure your Telegram bot token (if you want to use the bot)"
echo "2. Change the default SSH port for better security"
echo "3. Create your first SSH user"
echo
echo "Thank you for using SSHPlus Pro!" 