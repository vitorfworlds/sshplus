#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import socket
import subprocess
from datetime import datetime

class ProxyManager:
    def __init__(self):
        self.config_path = 'config/proxy_settings.json'
        self.setup()
        
    def setup(self):
        """Configura o ambiente inicial"""
        os.makedirs('config', exist_ok=True)
        self.load_config()
        
    def load_config(self):
        """Carrega ou cria arquivo de configuração do proxy"""
        if not os.path.exists(self.config_path):
            default_config = {
                'proxy_port': 8080,
                'squid_config': '/etc/squid/squid.conf',
                'allowed_ports': [80, 443, 8080],
                'proxy_interface': 'eth0',
                'cache_size': '100 MB',
                'max_clients': 100
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
                
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
            
    def update_config(self, key, value):
        """Atualiza uma configuração específica"""
        self.config[key] = value
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
            
    def install_squid(self):
        """Instala e configura o Squid Proxy"""
        try:
            # Instalar Squid
            os.system('apt update')
            os.system('apt install -y squid')
            
            # Backup da configuração original
            if os.path.exists('/etc/squid/squid.conf'):
                os.system('cp /etc/squid/squid.conf /etc/squid/squid.conf.bak')
                
            # Criar nova configuração
            config = f"""# Configuração do Squid Proxy
http_port {self.config['proxy_port']}
visible_hostname sshplus-proxy

# ACL para portas permitidas
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

# Regras básicas
http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports
http_access allow localhost manager
http_access deny manager

# Cache
cache_mem {self.config['cache_size']}
maximum_object_size 128 MB
cache_dir ufs /var/spool/squid 100 16 256

# Outras configurações
coredump_dir /var/spool/squid
refresh_pattern ^ftp: 1440 20% 10080
refresh_pattern ^gopher: 1440 0% 1440
refresh_pattern -i (/cgi-bin/|\?) 0 0% 0
refresh_pattern . 0 20% 4320

# Permitir acesso local
http_access allow localhost
http_access deny all"""

            with open('/etc/squid/squid.conf', 'w') as f:
                f.write(config)
                
            # Reiniciar Squid
            os.system('systemctl restart squid')
            return True
            
        except Exception as e:
            print(f"Erro ao instalar Squid: {e}")
            return False
            
    def start_proxy(self):
        """Inicia o serviço do proxy"""
        try:
            os.system('systemctl start squid')
            return True
        except:
            return False
            
    def stop_proxy(self):
        """Para o serviço do proxy"""
        try:
            os.system('systemctl stop squid')
            return True
        except:
            return False
            
    def restart_proxy(self):
        """Reinicia o serviço do proxy"""
        try:
            os.system('systemctl restart squid')
            return True
        except:
            return False
            
    def check_status(self):
        """Verifica o status do proxy"""
        try:
            result = subprocess.run(['systemctl', 'status', 'squid'], 
                                  capture_output=True, text=True)
            return result.stdout
        except:
            return "Erro ao verificar status"
            
    def add_port(self, port):
        """Adiciona uma nova porta permitida"""
        if port not in self.config['allowed_ports']:
            self.config['allowed_ports'].append(port)
            self.update_config('allowed_ports', self.config['allowed_ports'])
            return True
        return False
        
    def remove_port(self, port):
        """Remove uma porta permitida"""
        if port in self.config['allowed_ports']:
            self.config['allowed_ports'].remove(port)
            self.update_config('allowed_ports', self.config['allowed_ports'])
            return True
        return False
        
    def get_connections(self):
        """Retorna as conexões ativas no proxy"""
        try:
            result = subprocess.run(['netstat', '-tnp', '|', 'grep', 'squid'],
                                  capture_output=True, text=True, shell=True)
            return result.stdout
        except:
            return "Erro ao obter conexões"
            
class ProxyMenu:
    def __init__(self):
        self.manager = ProxyManager()
        self.options = {
            1: self.install_proxy,
            2: self.start_proxy,
            3: self.stop_proxy,
            4: self.restart_proxy,
            5: self.status_proxy,
            6: self.configure_proxy,
            7: self.manage_ports,
            8: self.view_connections,
            0: self.exit
        }
        
    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')
        
    def print_header(self):
        self.clear_screen()
        print("=" * 40)
        print("           PROXY MANAGER           ")
        print("=" * 40)
        
    def print_menu(self):
        self.print_header()
        print("\nEscolha uma opção:")
        print("1. Instalar Proxy")
        print("2. Iniciar Proxy")
        print("3. Parar Proxy")
        print("4. Reiniciar Proxy")
        print("5. Status do Proxy")
        print("6. Configurar Proxy")
        print("7. Gerenciar Portas")
        print("8. Ver Conexões")
        print("0. Sair")
        print("\n" + "=" * 40)
        
    def install_proxy(self):
        self.print_header()
        print("\nInstalando Proxy...")
        if self.manager.install_squid():
            print("Proxy instalado com sucesso!")
        else:
            print("Erro ao instalar proxy!")
        input("\nPressione ENTER para continuar...")
        
    def start_proxy(self):
        self.print_header()
        print("\nIniciando Proxy...")
        if self.manager.start_proxy():
            print("Proxy iniciado com sucesso!")
        else:
            print("Erro ao iniciar proxy!")
        input("\nPressione ENTER para continuar...")
        
    def stop_proxy(self):
        self.print_header()
        print("\nParando Proxy...")
        if self.manager.stop_proxy():
            print("Proxy parado com sucesso!")
        else:
            print("Erro ao parar proxy!")
        input("\nPressione ENTER para continuar...")
        
    def restart_proxy(self):
        self.print_header()
        print("\nReiniciando Proxy...")
        if self.manager.restart_proxy():
            print("Proxy reiniciado com sucesso!")
        else:
            print("Erro ao reiniciar proxy!")
        input("\nPressione ENTER para continuar...")
        
    def status_proxy(self):
        self.print_header()
        print("\nStatus do Proxy:")
        print("-" * 40)
        print(self.manager.check_status())
        input("\nPressione ENTER para continuar...")
        
    def configure_proxy(self):
        while True:
            self.print_header()
            print("\nConfigurar Proxy")
            print("-" * 40)
            print("1. Alterar porta do proxy")
            print("2. Alterar tamanho do cache")
            print("3. Alterar número máximo de clientes")
            print("4. Alterar interface")
            print("0. Voltar")
            
            option = input("\nEscolha uma opção: ")
            
            if option == "1":
                port = int(input("\nNova porta do proxy: "))
                self.manager.update_config('proxy_port', port)
                print("\nPorta atualizada com sucesso!")
                
            elif option == "2":
                size = input("\nNovo tamanho do cache (ex: 100 MB): ")
                self.manager.update_config('cache_size', size)
                print("\nTamanho do cache atualizado com sucesso!")
                
            elif option == "3":
                clients = int(input("\nNovo número máximo de clientes: "))
                self.manager.update_config('max_clients', clients)
                print("\nNúmero de clientes atualizado com sucesso!")
                
            elif option == "4":
                interface = input("\nNova interface (ex: eth0): ")
                self.manager.update_config('proxy_interface', interface)
                print("\nInterface atualizada com sucesso!")
                
            elif option == "0":
                break
                
            if option in ["1", "2", "3", "4"]:
                self.manager.restart_proxy()
                
            input("\nPressione ENTER para continuar...")
            
    def manage_ports(self):
        while True:
            self.print_header()
            print("\nGerenciar Portas")
            print("-" * 40)
            print("Portas permitidas:", self.manager.config['allowed_ports'])
            print("\n1. Adicionar porta")
            print("2. Remover porta")
            print("0. Voltar")
            
            option = input("\nEscolha uma opção: ")
            
            if option == "1":
                port = int(input("\nNova porta: "))
                if self.manager.add_port(port):
                    print("\nPorta adicionada com sucesso!")
                else:
                    print("\nPorta já existe!")
                    
            elif option == "2":
                port = int(input("\nPorta para remover: "))
                if self.manager.remove_port(port):
                    print("\nPorta removida com sucesso!")
                else:
                    print("\nPorta não encontrada!")
                    
            elif option == "0":
                break
                
            if option in ["1", "2"]:
                self.manager.restart_proxy()
                
            input("\nPressione ENTER para continuar...")
            
    def view_connections(self):
        self.print_header()
        print("\nConexões Ativas:")
        print("-" * 40)
        print(self.manager.get_connections())
        input("\nPressione ENTER para continuar...")
        
    def exit(self):
        self.print_header()
        print("\nEncerrando Proxy Manager...")
        sys.exit(0)
        
    def run(self):
        while True:
            self.print_menu()
            try:
                option = int(input("\nOpção: "))
                if option in self.options:
                    self.options[option]()
                else:
                    print("\nOpção inválida!")
                    time.sleep(2)
            except ValueError:
                print("\nOpção inválida!")
                time.sleep(2)
                
if __name__ == "__main__":
    menu = ProxyMenu()
    menu.run() 