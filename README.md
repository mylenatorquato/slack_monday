# 📡 Notificações Automatizadas do Monday.com para Slack

Este script monitora subitens de um board no [Monday.com](https://monday.com) e envia notificações para um canal do Slack sempre que:

- Um novo **subitem** é criado em grupos específicos.
- O **status** de um subitem for alterado para "Feito" ou "Pausado".

## ⚙️ Pré-requisitos

- Conta no [Monday.com](https://monday.com)
- Webhook configurado no [Slack](https://api.slack.com/apps)
- Python 3.x
- Bibliotecas: `requests`

```bash
pip install requests
```

## 🔐 Configuração

Antes de executar o script, você precisa configurar o arquivo `config.py` com suas credenciais e IDs corretos:

```python
# config.py

API_KEY = "SEU_TOKEN_DA_API_MONDAY"
SLACK_WEBHOOK = "https://hooks.slack.com/services/SEU/WEBHOOK/URL"
MONDAY_DOMAIN = "https://sua-conta.monday.com"

# IDs dos grupos permitidos
ALLOWED_GROUPS_IDS = ["topics", "dry", "clientes"]

# Arquivos locais usados para controle de estado
ARQ_CRIADOS = "criados.json"
ARQ_STATUS = "status.json"
ARQ_INICIALIZADO = "iniciado.txt"

# URL da API do Monday
API_URL = "https://api.monday.com/v2"

# ID da coluna de status
STATUS_COLUMN_ID = "status"
```

## 🚀 Como usar

Execute o script com:

```bash
python notificacao_create_status.py
```

Na primeira execução, o sistema inicializa os arquivos locais e **não envia notificações**. A partir da segunda execução, todas as alterações relevantes serão notificadas automaticamente no Slack.

## 🔁 O que ele faz

Este script deve ser executado periodicamente via cron (ou qualquer outro agendador de tarefas). Em cada execução, ele:

  - Busca todos os subitens de um board específico no Monday.com.

  - Verifica se o subitem já foi notificado anteriormente (criação).

  - Verifica se o status foi alterado desde a última execução.

  - Envia uma notificação para o Slack caso detecte:

      - Um subitem recém-criado.

      - Uma mudança de status para FEITO ou PAUSADO.

## 📦 Organização do Projeto

```
├── notificacao_create_status.py
├── config.py
├── criados.json
├── status.json
├── iniciado.txt
└── README.md
```
