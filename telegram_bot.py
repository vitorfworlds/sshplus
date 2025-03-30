#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import logging
import sqlite3
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

class TelegramBot:
    def __init__(self):
        self.config_path = 'config/bot_settings.json'
        self.setup()
        
    def setup(self):
        """Configura o ambiente inicial"""
        os.makedirs('config', exist_ok=True)
        self.load_config()
        
        # Configurar logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        
    def load_config(self):
        """Carrega ou cria arquivo de configuração do bot"""
        if not os.path.exists(self.config_path):
            default_config = {
                'token': 'SEU_TOKEN_AQUI',
                'admin_users': [],
                'welcome_message': 'Bem-vindo ao SSHPlus Bot!',
                'help_message': 'Use /help para ver os comandos disponíveis',
                'unauthorized_message': 'Você não tem permissão para usar este bot'
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
                
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
            
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user_id = update.effective_user.id
        if user_id not in self.config['admin_users']:
            await update.message.reply_text(self.config['unauthorized_message'])
            return
            
        keyboard = [
            [
                InlineKeyboardButton("👥 Usuários", callback_data='users'),
                InlineKeyboardButton("📊 Status", callback_data='status')
            ],
            [
                InlineKeyboardButton("🔧 Configurações", callback_data='settings'),
                InlineKeyboardButton("❓ Ajuda", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(self.config['welcome_message'], reply_markup=reply_markup)
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        user_id = update.effective_user.id
        if user_id not in self.config['admin_users']:
            await update.message.reply_text(self.config['unauthorized_message'])
            return
            
        help_text = """
Comandos disponíveis:

/start - Iniciar o bot
/help - Mostrar esta ajuda
/users - Gerenciar usuários
/status - Ver status do sistema
/settings - Configurações do sistema
/adduser - Adicionar novo usuário
/deluser - Remover usuário
/listusers - Listar usuários
/checkuser - Verificar usuário
/proxy - Gerenciar proxy
"""
        await update.message.reply_text(help_text)
        
    async def users_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menu de gerenciamento de usuários"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Adicionar", callback_data='adduser'),
                InlineKeyboardButton("➖ Remover", callback_data='deluser')
            ],
            [
                InlineKeyboardButton("📋 Listar", callback_data='listusers'),
                InlineKeyboardButton("🔍 Verificar", callback_data='checkuser')
            ],
            [
                InlineKeyboardButton("🔙 Voltar", callback_data='back')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Gerenciamento de Usuários", reply_markup=reply_markup)
        
    async def status_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menu de status do sistema"""
        query = update.callback_query
        await query.answer()
        
        # Obter informações do sistema
        try:
            conn = sqlite3.connect('database/users.db')
            c = conn.cursor()
            
            c.execute('SELECT COUNT(*) FROM users')
            total_users = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM active_connections')
            active_connections = c.fetchone()[0]
            
            conn.close()
            
            # Informações do sistema
            memory = os.popen('free -h').readlines()[1].split()
            cpu = os.popen('top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\\1/" | awk \'{print 100 - $1"%"}\'').read().strip()
            disk = os.popen('df -h / | tail -1').split()
            
            status_text = f"""
📊 Status do Sistema:

👥 Usuários: {total_users}
🔌 Conexões Ativas: {active_connections}

💻 Sistema:
CPU: {cpu}
RAM: {memory[2]} / {memory[1]}
Disco: {disk[3]} / {disk[1]} ({disk[4]})
"""
        except Exception as e:
            status_text = f"Erro ao obter status: {e}"
            
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(status_text, reply_markup=reply_markup)
        
    async def settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menu de configurações"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [
                InlineKeyboardButton("🔑 Limite de Conexões", callback_data='setconn'),
                InlineKeyboardButton("🌐 Limite de IPs", callback_data='setip')
            ],
            [
                InlineKeyboardButton("⏰ Tempo de Bloqueio", callback_data='setblock'),
                InlineKeyboardButton("🔄 Reiniciar Serviços", callback_data='restart')
            ],
            [
                InlineKeyboardButton("🔙 Voltar", callback_data='back')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Configurações do Sistema", reply_markup=reply_markup)
        
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manipulador de botões inline"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'users':
            await self.users_menu(update, context)
        elif query.data == 'status':
            await self.status_menu(update, context)
        elif query.data == 'settings':
            await self.settings_menu(update, context)
        elif query.data == 'help':
            await self.help_command(update, context)
        elif query.data == 'back':
            await self.start(update, context)
            
    def run(self):
        """Inicia o bot"""
        app = Application.builder().token(self.config['token']).build()
        
        # Adicionar handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Iniciar o bot
        print("Bot iniciado! Pressione Ctrl+C para parar.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
if __name__ == "__main__":
    bot = TelegramBot()
    bot.run() 