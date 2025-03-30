# SSHPlus Manager

Sistema de gerenciamento de usuários SSH com proxy integrado e bot do Telegram.

## Características

- Gerenciamento de usuários SSH
- Controle de conexões e IPs
- Proxy integrado (Squid)
- Bot do Telegram para gerenciamento remoto
- Interface de linha de comando amigável
- Sistema de monitoramento em tempo real

## Requisitos

- Sistema operacional Linux (Ubuntu/Debian recomendado)
- Python 3.7 ou superior
- Acesso root

## Instalação

1. Baixe o instalador:
```bash
wget https://raw.githubusercontent.com/seu-usuario/sshplus/main/install.sh
```

2. Dê permissão de execução:
```bash
chmod +x install.sh
```

3. Execute o instalador:
```bash
./install.sh
```

## Uso

### Menu Principal
Para acessar o menu principal:
```bash
menu
```

### Gerenciador de Proxy
Para acessar o gerenciador de proxy:
```bash
proxy
```

### Bot do Telegram
1. Edite o arquivo de configuração:
```bash
nano /opt/sshplus/config/bot_settings.json
```

2. Configure seu token e usuários admin:
```json
{
    "token": "SEU_TOKEN_AQUI",
    "admin_users": [123456789],
    "welcome_message": "Bem-vindo ao SSHPlus Bot!"
}
```

## Comandos Principais

- `menu` - Acessar menu principal
- `proxy` - Gerenciar proxy
- `adduser` - Adicionar usuário
- `deluser` - Remover usuário
- `listusers` - Listar usuários
- `checkuser` - Verificar usuário

## Configurações

### SSH
O arquivo de configuração SSH está em:
```
/etc/ssh/sshd_config
```

### Proxy
O arquivo de configuração do proxy está em:
```
/etc/squid/squid.conf
```

### Bot
O arquivo de configuração do bot está em:
```
/opt/sshplus/config/bot_settings.json
```

## Gerenciamento de Usuários

### Adicionar Usuário
```bash
menu
# Selecione opção 1
```

### Remover Usuário
```bash
menu
# Selecione opção 2
```

### Listar Usuários
```bash
menu
# Selecione opção 3
```

## Monitoramento

### Conexões Ativas
```bash
menu
# Selecione opção 5
```

### Status do Sistema
```bash
menu
# Selecione opção 4
```

## Segurança

- Todas as senhas são armazenadas com criptografia
- Sistema de bloqueio automático de IPs suspeitos
- Limite de conexões por usuário
- Limite de IPs por usuário
- Registro de todas as atividades

## Suporte

Para suporte, abra uma issue no GitHub ou entre em contato através do Telegram.

## Contribuindo

1. Fork o projeto
2. Crie sua branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Créditos

Desenvolvido por [Seu Nome] 