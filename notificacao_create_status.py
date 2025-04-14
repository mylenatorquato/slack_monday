import requests
import json
import time
import os

from config import (
    API_KEY,
    SLACK_WEBHOOK,
    MONDAY_DOMAIN,
    ALLOWED_GROUPS_IDS,
    ARQ_CRIADOS,
    ARQ_STATUS,
    ARQ_INICIALIZADO,
    API_URL,
    STATUS_COLUMN_ID,
)

HEADERS = {"Authorization": API_KEY, "Content-Type": "application/json"}

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return set(json.load(f)) if filename == ARQ_CRIADOS else json.load(f)
    return set() if filename == ARQ_CRIADOS else {}

def graphql(query):
    response = requests.post(API_URL, headers=HEADERS, json={"query": query})
    try:
        data = response.json()
    except Exception as e:
        raise Exception(f"Erro ao converter JSON: {e}\n{response.text}")
    if "errors" in data:
        raise Exception(f"Erros da API: {json.dumps(data['errors'], indent=2)}")
    return data

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

def send_created_notification(user_name, item_name, subitem_name, group_name, subitem_id):
    subitem_url = f"{MONDAY_DOMAIN}/boards/xx/pulses/{subitem_id}"
    payload = {
        "text": f" *{group_name}*: *{user_name}* adicionou *{subitem_name}* no item *{item_name}*\n\nVeja na Monday: {subitem_url}"
    }
    requests.post(SLACK_WEBHOOK, json=payload)

def send_status_notification(user_name, item_name, subitem_name, status, group_name, subitem_id):
    subitem_url = f"{MONDAY_DOMAIN}/boards/xx/pulses/{subitem_id}"
    emoji = ":white_check_mark:" if status == "FEITO" else "🛑"
    payload = {
        "text": f"{emoji} *{group_name}*: {user_name} mudou para *{status}* o usuário *{subitem_name}* do item *{item_name}*\n\nVeja na Monday: {subitem_url}"
    }
    requests.post(SLACK_WEBHOOK, json=payload)

def get_subitems():
    all_items = []
    cursor = None

    while True:
        cursor_str = f', cursor: "{cursor}"' if cursor else ""
        query = f"""
        {{
            boards (ids: xx) {{
                items_page(limit: 100{cursor_str}) {{
                    cursor
                    items {{
                        name
                        id
                        group {{
                            id
                            title
                        }}
                        subitems {{
                            id
                            name
                            creator {{
                                name
                            }}
                            column_values {{
                                id
                                type
                                text
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        data = graphql(query)
        page = data["data"]["boards"][0]["items_page"]
        items = page["items"]
        all_items.extend(items)

        cursor = page.get("cursor")
        if not cursor:
            break

    return all_items

def main():
    notified_creations = load_json(ARQ_CRIADOS)
    status_notifications = load_json(ARQ_STATUS)

    if isinstance(notified_creations, list):
        notified_creations = set(notified_creations)

    primeira_execucao = not os.path.exists(ARQ_INICIALIZADO)

    novos_criados = 0
    status_alterados = 0

    items = get_subitems()
    if not items:
        return

    for item in items:
        current_group = item.get("group", {}).get("id")
        group_name = item.get("group", {}).get("title", "Grupo")

        if current_group not in ALLOWED_GROUPS_IDS:
            continue

        for sub in item.get("subitems", []):
            sub_id = sub["id"]
            user_name = sub.get("creator", {}).get("name", "Desconhecido")
            item_name = item["name"]
            subitem_name = sub["name"]

            if sub_id not in notified_creations:
                if not primeira_execucao:
                    send_created_notification(user_name, item_name, subitem_name, group_name, sub_id)
                    novos_criados += 1
                notified_creations.add(sub_id)

            current_status = None
            for column in sub.get("column_values", []):
                if column.get("id") == STATUS_COLUMN_ID or column.get("type") == "color":
                    current_status = column.get("text")
                    break

            if current_status:
                current_status = current_status.upper()
                if current_status in ["FEITO", "PAUSADO"]:
                    last_status = status_notifications.get(sub_id)
                    if last_status != current_status:
                        if not primeira_execucao:
                            send_status_notification(user_name, item_name, subitem_name, current_status, group_name, sub_id)
                            status_alterados += 1
                        status_notifications[sub_id] = current_status

    save_json(ARQ_CRIADOS, list(notified_creations))
    save_json(ARQ_STATUS, status_notifications)

    if primeira_execucao:
        with open(ARQ_INICIALIZADO, "w") as f:
            f.write("iniciado")

if __name__ == "__main__":
    main()
