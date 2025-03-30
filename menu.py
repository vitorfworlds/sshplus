#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
from datetime import datetime
from sshplus_manager import SSHPlusManager
from proxy_manager import ProxyManager
from optimization import NetworkOptimizer
from v2ray_manager import V2RayManager
from backup_manager import BackupManager
from banner_manager import BannerManager
import logging

class SSHPlusMenu:
    def __init__(self):
        self.ssh_manager = SSHPlusManager()
        self.proxy_manager = ProxyManager()
        self.network_optimizer = NetworkOptimizer()
        self.v2ray_manager = V2RayManager()
        self.backup_manager = BackupManager()
        self.banner_manager = BannerManager()
        
        self.options = {
            "1": self.users_menu,
            "2": self.connections_menu,
            "3": self.proxy_menu,
            "4": self.v2ray_menu,
            "5": self.optimization_menu,
            "6": self.backup_menu,
            "7": self.banner_menu,
            "8": self.settings_menu,
            "0": self.exit
        }
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear')
    
    def print_header(self):
        """Print menu header"""
        self.clear_screen()
        print("=" * 40)
        print("        SSHPlus Pro Manager")
        print("=" * 40)
        print()
    
    def print_menu(self):
        """Print main menu options"""
        self.print_header()
        print("1. User Management")
        print("2. Connection Monitor")
        print("3. Proxy Settings")
        print("4. V2Ray Manager")
        print("5. Optimization Tools")
        print("6. Backup & Restore")
        print("7. Banner Settings")
        print("8. System Settings")
        print("0. Exit")
        print()
    
    def users_menu(self):
        """User management submenu"""
        while True:
            self.print_header()
            print("=== User Management ===")
            print("1. Add User")
            print("2. Remove User")
            print("3. List Users")
            print("4. Check User")
            print("5. Set User Limits")
            print("0. Back")
            print()
            
            choice = input("Choose an option: ")
            
            if choice == "1":
                username = input("Username: ")
                password = input("Password: ")
                days = int(input("Days until expiration: "))
                max_connections = int(input("Max connections: "))
                max_ips = int(input("Max IPs: "))
                
                success, message = self.ssh_manager.add_user(
                    username, password, days, max_connections, max_ips
                )
                print(message)
            
            elif choice == "2":
                username = input("Username to remove: ")
                confirm = input(f"Confirm removal of user {username}? (y/n): ")
                
                if confirm.lower() == 'y':
                    success, message = self.ssh_manager.remove_user(username)
                    print(message)
            
            elif choice == "3":
                success, users = self.ssh_manager.list_users()
                if success:
                    print("\nUser List:")
                    for user in users:
                        print(f"Username: {user['username']}")
                        print(f"Expires: {user['expiry_date']}")
                        print(f"Max Connections: {user['max_connections']}")
                        print(f"Max IPs: {user['max_ips']}")
                        print("-" * 20)
            
            elif choice == "4":
                username = input("Username to check: ")
                success, info = self.ssh_manager.check_user(username)
                if success:
                    print(f"\nUser Information for {username}:")
                    print(f"Status: {info['status']}")
                    print(f"Expiry Date: {info['expiry_date']}")
                    print(f"Active Connections: {info['active_connections']}")
                    print(f"Used IPs: {info['used_ips']}")
            
            elif choice == "5":
                username = input("Username: ")
                max_connections = int(input("New max connections (0 for unlimited): "))
                max_ips = int(input("New max IPs (0 for unlimited): "))
                
                success, message = self.ssh_manager.set_user_limits(
                    username, max_connections, max_ips
                )
                print(message)
            
            elif choice == "0":
                break
    
    def connections_menu(self):
        """Connection monitoring submenu"""
        while True:
            self.print_header()
            print("=== Connection Monitor ===")
            print("1. Show Active Connections")
            print("2. Monitor Real-time")
            print("3. Kill Connection")
            print("0. Back")
            print()
            
            choice = input("Choose an option: ")
            
            if choice == "1":
                success, connections = self.ssh_manager.get_active_connections()
                if success:
                    print("\nActive Connections:")
                    for conn in connections:
                        print(f"User: {conn['username']}")
                        print(f"IP: {conn['ip']}")
                        print(f"Connected since: {conn['connected_since']}")
                        print("-" * 20)
            
            elif choice == "2":
                try:
                    print("Monitoring connections (Ctrl+C to stop)...")
                    while True:
                        self.clear_screen()
                        success, connections = self.ssh_manager.get_active_connections()
                        if success:
                            print("\nActive Connections:")
                            for conn in connections:
                                print(f"User: {conn['username']}")
                                print(f"IP: {conn['ip']}")
                                print(f"Connected since: {conn['connected_since']}")
                                print("-" * 20)
                        time.sleep(5)
                except KeyboardInterrupt:
                    pass
            
            elif choice == "3":
                username = input("Username: ")
                ip = input("IP (leave empty for all): ")
                
                success, message = self.ssh_manager.kill_connection(username, ip)
                print(message)
            
            elif choice == "0":
                break
    
    def proxy_menu(self):
        """Proxy settings submenu"""
        while True:
            self.print_header()
            print("=== Proxy Settings ===")
            print("1. Install Squid")
            print("2. Start Proxy")
            print("3. Stop Proxy")
            print("4. Restart Proxy")
            print("5. Add Port")
            print("6. Remove Port")
            print("7. Show Status")
            print("0. Back")
            print()
            
            choice = input("Choose an option: ")
            
            if choice == "1":
                success, message = self.proxy_manager.install_squid()
                print(message)
            
            elif choice == "2":
                success, message = self.proxy_manager.start_proxy()
                print(message)
            
            elif choice == "3":
                success, message = self.proxy_manager.stop_proxy()
                print(message)
            
            elif choice == "4":
                success, message = self.proxy_manager.restart_proxy()
                print(message)
            
            elif choice == "5":
                port = int(input("New port: "))
                success, message = self.proxy_manager.add_port(port)
                print(message)
            
            elif choice == "6":
                port = int(input("Port to remove: "))
                success, message = self.proxy_manager.remove_port(port)
                print(message)
            
            elif choice == "7":
                success, status = self.proxy_manager.check_status()
                if success:
                    print("\nProxy Status:")
                    print(f"Running: {status['running']}")
                    print(f"Active Ports: {', '.join(map(str, status['ports']))}")
                    print(f"Active Connections: {status['connections']}")
            
            elif choice == "0":
                break
    
    def v2ray_menu(self):
        """V2Ray management submenu"""
        while True:
            self.print_header()
            print("=== V2Ray Manager ===")
            print("1. Install V2Ray")
            print("2. Add User")
            print("3. Remove User")
            print("4. List Users")
            print("5. Show Configuration")
            print("0. Back")
            print()
            
            choice = input("Choose an option: ")
            
            if choice == "1":
                success, message = self.v2ray_manager.install_v2ray()
                print(message)
            
            elif choice == "2":
                username = input("Username: ")
                email = input("Email (optional): ")
                
                success, result = self.v2ray_manager.add_user(username, email)
                if success:
                    print("\nUser added successfully!")
                    print(f"VMess URL: {result['vmess_url']}")
                    print("\nClient Configuration:")
                    for key, value in result['client_config'].items():
                        print(f"{key}: {value}")
            
            elif choice == "3":
                username = input("Username to remove: ")
                success, message = self.v2ray_manager.remove_user(username)
                print(message)
            
            elif choice == "4":
                success, users = self.v2ray_manager.list_users()
                if success:
                    print("\nV2Ray Users:")
                    for user in users:
                        print(f"Username: {user['username']}")
                        print(f"Email: {user['email']}")
                        print(f"UUID: {user['id']}")
                        print(f"Enabled: {user['enabled']}")
                        print("-" * 20)
            
            elif choice == "0":
                break
    
    def optimization_menu(self):
        """Network optimization submenu"""
        while True:
            self.print_header()
            print("=== Optimization Tools ===")
            print("1. Install BadVPN")
            print("2. Install TCP Tweaker")
            print("3. Run Speed Test")
            print("4. Set User Speed Limit")
            print("5. Remove Speed Limit")
            print("0. Back")
            print()
            
            choice = input("Choose an option: ")
            
            if choice == "1":
                success, message = self.network_optimizer.install_badvpn()
                print(message)
            
            elif choice == "2":
                success, message = self.network_optimizer.install_tcp_tweaker()
                print(message)
            
            elif choice == "3":
                print("Running speed test...")
                success, result = self.network_optimizer.run_speedtest()
                if success:
                    print(f"\nSpeed Test Results:")
                    print(f"Download: {result['download']} Mbps")
                    print(f"Upload: {result['upload']} Mbps")
                    print(f"Ping: {result['ping']} ms")
                    print(f"Server: {result['server']}")
            
            elif choice == "4":
                username = input("Username: ")
                download = float(input("Download limit (Mbps): "))
                upload = float(input("Upload limit (Mbps): "))
                
                success, message = self.network_optimizer.set_user_speed_limit(
                    username, download, upload
                )
                print(message)
            
            elif choice == "5":
                username = input("Username: ")
                success, message = self.network_optimizer.remove_user_speed_limit(username)
                print(message)
            
            elif choice == "0":
                break
    
    def backup_menu(self):
        """Backup and restore submenu"""
        while True:
            self.print_header()
            print("=== Backup & Restore ===")
            print("1. Create Backup")
            print("2. Restore Backup")
            print("3. List Backups")
            print("4. Delete Backup")
            print("0. Back")
            print()
            
            choice = input("Choose an option: ")
            
            if choice == "1":
                name = input("Backup name (optional): ")
                success, result = self.backup_manager.create_backup(name)
                if success:
                    print(f"\nBackup created successfully!")
                    print(f"File: {result['backup_file']}")
                    print(f"Size: {result['size']} bytes")
                    print(f"Created: {result['timestamp']}")
            
            elif choice == "2":
                success, backups = self.backup_manager.list_backups()
                if success and backups:
                    print("\nAvailable backups:")
                    for i, backup in enumerate(backups, 1):
                        print(f"{i}. {backup['name']}")
                    
                    choice = int(input("\nChoose backup to restore: ")) - 1
                    if 0 <= choice < len(backups):
                        confirm = input("This will overwrite current configuration. Continue? (y/n): ")
                        if confirm.lower() == 'y':
                            success, message = self.backup_manager.restore_backup(backups[choice]['path'])
                            print(message)
            
            elif choice == "3":
                success, backups = self.backup_manager.list_backups()
                if success:
                    print("\nAvailable backups:")
                    for backup in backups:
                        print(f"Name: {backup['name']}")
                        print(f"Size: {backup['size']} bytes")
                        print(f"Created: {backup['created']}")
                        print("-" * 20)
            
            elif choice == "4":
                success, backups = self.backup_manager.list_backups()
                if success and backups:
                    print("\nAvailable backups:")
                    for i, backup in enumerate(backups, 1):
                        print(f"{i}. {backup['name']}")
                    
                    choice = int(input("\nChoose backup to delete: ")) - 1
                    if 0 <= choice < len(backups):
                        success, message = self.backup_manager.delete_backup(backups[choice]['name'])
                        print(message)
            
            elif choice == "0":
                break
    
    def banner_menu(self):
        """Banner customization submenu"""
        while True:
            self.print_header()
            print("=== Banner Settings ===")
            print("1. Set Banner Message")
            print("2. Change Banner Style")
            print("3. Set MOTD")
            print("4. Toggle System Info")
            print("5. Toggle User Info")
            print("0. Back")
            print()
            
            choice = input("Choose an option: ")
            
            if choice == "1":
                message = input("Enter banner message: ")
                success, result = self.banner_manager.set_banner(message=message)
                print(result)
            
            elif choice == "2":
                print("\nAvailable styles:")
                print("1. Default")
                print("2. ASCII Art")
                
                style_choice = input("Choose style: ")
                style = "default" if style_choice == "1" else "ascii"
                
                success, result = self.banner_manager.set_banner(style=style)
                print(result)
            
            elif choice == "3":
                message = input("Enter MOTD message: ")
                success, result = self.banner_manager.set_motd(message)
                print(result)
            
            elif choice == "4":
                show = input("Show system information? (y/n): ").lower() == 'y'
                success, result = self.banner_manager.toggle_system_info(show)
                print(result)
            
            elif choice == "5":
                show = input("Show user information? (y/n): ").lower() == 'y'
                success, result = self.banner_manager.toggle_user_info(show)
                print(result)
            
            elif choice == "0":
                break
    
    def settings_menu(self):
        """System settings submenu"""
        while True:
            self.print_header()
            print("=== System Settings ===")
            print("1. Change SSH Port")
            print("2. Change Admin Password")
            print("3. Update System")
            print("4. View Logs")
            print("0. Back")
            print()
            
            choice = input("Choose an option: ")
            
            if choice == "1":
                port = int(input("New SSH port: "))
                success, message = self.ssh_manager.change_ssh_port(port)
                print(message)
            
            elif choice == "2":
                old_pass = input("Current password: ")
                new_pass = input("New password: ")
                confirm_pass = input("Confirm new password: ")
                
                if new_pass == confirm_pass:
                    success, message = self.ssh_manager.change_admin_password(old_pass, new_pass)
                    print(message)
                else:
                    print("Passwords do not match!")
            
            elif choice == "3":
                confirm = input("This will update all system packages. Continue? (y/n): ")
                if confirm.lower() == 'y':
                    success, message = self.ssh_manager.update_system()
                    print(message)
            
            elif choice == "4":
                lines = int(input("Number of lines to show (0 for all): "))
                success, logs = self.ssh_manager.view_logs(lines)
                if success:
                    print("\nSystem Logs:")
                    print(logs)
            
            elif choice == "0":
                break
    
    def exit(self):
        """Exit the program"""
        print("\nThank you for using SSHPlus Pro!")
        sys.exit(0)
    
    def run(self):
        """Main menu loop"""
        while True:
            self.print_menu()
            choice = input("Choose an option: ")
            
            if choice in self.options:
                self.options[choice]()
                
if __name__ == "__main__":
    menu = SSHPlusMenu()
    menu.run() 