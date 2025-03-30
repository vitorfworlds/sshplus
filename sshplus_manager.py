#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import socket
import sqlite3
import subprocess
from datetime import datetime, timedelta

class SSHPlusManager:
    def __init__(self):
        self.db_path = 'database/users.db'
        self.config_path = 'config/settings.json'
        self.setup()
        
    def setup(self):
        """Configura o ambiente inicial"""
        # Criar diretórios necessários
        os.makedirs('database', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Inicializar banco de dados
        self.init_database()
        
        # Carregar ou criar configurações
        self.load_config()
        
    def init_database(self):
        """Inicializa o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Tabela de usuários
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (username TEXT PRIMARY KEY,
                     password TEXT,
                     expiry_date TEXT,
                     connection_limit INTEGER,
                     ip_limit INTEGER)''')
                     
        # Tabela de IPs
        c.execute('''CREATE TABLE IF NOT EXISTS ip_addresses
                    (ip TEXT,
                     username TEXT,
                     last_connection TEXT,
                     FOREIGN KEY(username) REFERENCES users(username))''')
                     
        # Tabela de conexões ativas
        c.execute('''CREATE TABLE IF NOT EXISTS active_connections
                    (username TEXT,
                     ip TEXT,
                     connected_since TEXT,
                     FOREIGN KEY(username) REFERENCES users(username))''')
        
        conn.commit()
        conn.close()
        
    def load_config(self):
        """Carrega ou cria arquivo de configuração"""
        if not os.path.exists(self.config_path):
            default_config = {
                'max_connections': 1,
                'max_ips_per_user': 1,
                'block_time': 3600,
                'ssh_port': 22,
                'admin_user': 'admin',
                'admin_pass': 'admin',
                'allow_duplicate_ips': False,
                'log_level': 'INFO'
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
                
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
            
    def add_user(self, username, password, days=30, conn_limit=1, ip_limit=1):
        """Adiciona um novo usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            expiry = datetime.now() + timedelta(days=days)
            expiry = expiry.strftime('%Y-%m-%d %H:%M:%S')
            
            c.execute('INSERT INTO users VALUES (?,?,?,?,?)',
                     (username, password, expiry, conn_limit, ip_limit))
            
            # Criar usuário no sistema
            os.system(f'useradd -M -s /bin/false {username}')
            os.system(f'echo "{username}:{password}" | chpasswd')
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar usuário: {e}")
            return False
        finally:
            conn.close()
            
    def remove_user(self, username):
        """Remove um usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('DELETE FROM users WHERE username = ?', (username,))
            c.execute('DELETE FROM ip_addresses WHERE username = ?', (username,))
            c.execute('DELETE FROM active_connections WHERE username = ?', (username,))
            
            # Remover usuário do sistema
            os.system(f'userdel {username}')
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao remover usuário: {e}")
            return False
        finally:
            conn.close()
            
    def check_connection(self, username, ip):
        """Verifica se uma conexão é permitida"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Verificar se usuário existe e não está expirado
        c.execute('SELECT expiry_date, connection_limit, ip_limit FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        
        if not user:
            return False, "Usuário não existe"
            
        expiry = datetime.strptime(user[0], '%Y-%m-%d %H:%M:%S')
        if expiry < datetime.now():
            return False, "Usuário expirado"
            
        # Verificar limite de conexões
        c.execute('SELECT COUNT(*) FROM active_connections WHERE username = ?', (username,))
        active_conns = c.fetchone()[0]
        
        if active_conns >= user[1]:
            return False, "Limite de conexões atingido"
            
        # Verificar limite de IPs
        c.execute('SELECT COUNT(DISTINCT ip) FROM ip_addresses WHERE username = ?', (username,))
        ip_count = c.fetchone()[0]
        
        if ip_count >= user[2] and ip not in [row[0] for row in c.execute('SELECT ip FROM ip_addresses WHERE username = ?', (username,))]:
            return False, "Limite de IPs atingido"
            
        return True, "Conexão permitida"
        
    def monitor_connections(self):
        """Monitora conexões ativas"""
        while True:
            # Verificar processos SSH
            ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
            processes = ps.decode().split('\n')
            
            active_users = []
            for process in processes:
                if 'sshd:' in process and '@' in process:
                    user = process.split('@')[0].split(':')[1].strip()
                    active_users.append(user)
                    
            # Atualizar banco de dados
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Limpar conexões antigas
            c.execute('DELETE FROM active_connections')
            
            # Inserir conexões atuais
            for user in active_users:
                c.execute('INSERT INTO active_connections VALUES (?,?,?)',
                         (user, '0.0.0.0', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                         
            conn.commit()
            conn.close()
            
            time.sleep(60)  # Verificar a cada minuto

    def start(self):
        """Inicia o gerenciador"""
        print("SSHPlus Manager iniciado")
        try:
            self.monitor_connections()
        except KeyboardInterrupt:
            print("\nEncerrando SSHPlus Manager...")
            sys.exit(0)

if __name__ == "__main__":
    manager = SSHPlusManager()
    manager.start() 