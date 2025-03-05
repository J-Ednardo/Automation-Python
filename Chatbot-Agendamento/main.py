from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configurações
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0/YOUR_PHONE_NUMBER_ID/messages"
WHATSAPP_TOKEN = "YOUR_WHATSAPP_ACCESS_TOKEN"
CALENDLY_WEBHOOK_SECRET = "YOUR_CALENDLY_SECRET"
PIPEFY_API_URL = "https://api.pipefy.com/graphql"
PIPEFY_TOKEN = "YOUR_PIPEFY_ACCESS_TOKEN"
CALENDLY_LINK = "https://calendly.com/YOUR_SCHEDULE_LINK"
PIPE_ID = "YOUR_PIPEFY_PIPE_ID"

# Rota Webhook do WhatsApp
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.get_json()
    if data and "messages" in data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}):
        sender = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        send_whatsapp_message(sender, "Olá! Agende um horário aqui: " + CALENDLY_LINK)
    return jsonify({"status": "success"})

# Enviar mensagem no WhatsApp
def send_whatsapp_message(to, message):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    requests.post(WHATSAPP_API_URL, json=payload, headers=headers)

# Webhook do Calendly
@app.route("/calendly-webhook", methods=["POST"])
def calendly_webhook():
    data = request.get_json()
    if data.get("event") == "invitee.created":
        invitee_data = data.get("payload", {}).get("invitee", {})
        name = invitee_data.get("name")
        email = invitee_data.get("email")
        event_start_time = data.get("payload", {}).get("event", {}).get("start_time")
        create_pipefy_card(name, email, event_start_time)
    return jsonify({"status": "received"})

# Criar Card no Pipefy
def create_pipefy_card(name, email, date):
    headers = {
        "Authorization": f"Bearer {PIPEFY_TOKEN}",
        "Content-Type": "application/json"
    }
    query = {
        "query": f"""
        mutation {{
            createCard(input: {{ pipe_id: {PIPE_ID}, fields_attributes: [
                {{field_id: "nome", field_value: "{name}"}},
                {{field_id: "email", field_value: "{email}"}},
                {{field_id: "data", field_value: "{date}"}}
            ] }}) {{ card {{ id title }} }}
        }}
        """
    }
    requests.post(PIPEFY_API_URL, json=query, headers=headers)

if __name__ == "__main__":
    app.run(port=5000, debug=True)