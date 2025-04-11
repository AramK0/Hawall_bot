from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import logging
import requests 

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Facebook tokens
VERIFY_TOKEN = "my_secret_token"  # Use the same one you put in Facebook Dev settings
PAGE_ACCESS_TOKEN = "EAARNbuj5FZCkBO3UzTCo8puUhZCAZCYqqZBIiS3CFhgbsIV2bZCBGcfbex6E96UxasA9cofYvDA5OIii8q8JuHzZCdDE9ejnZBqZCDGLZCo3fLnsOk5huTwxmvRINnbFfE8NTZCAwablQnbDNW8HnjX6jtALgqGCsG1ZAmH8UhAdwEqaWZAwwB0XL2a0UG5d3tCPPoxfyJrxgsFTUv4xe3APMhCZBEMJfDgZDZD"  # Replace with your Page token

# ✅ GET /webhook - Used by Facebook to verify the webhook
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logging.info("✅ Webhook verified by Facebook.")
        return PlainTextResponse(content=challenge, status_code=200)
    else:
        logging.warning("❌ Webhook verification failed.")
        return PlainTextResponse(content="Verification failed", status_code=403)


# ✅ POST /webhook - Facebook sends messages here
@app.post("/webhook")
async def handle_incoming_webhook(request: Request):
    try:
        payload = await request.json()
        logging.info("📥 Received webhook payload: %s", payload)

        if payload.get("object") == "page":
            for entry in payload.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event.get("message", {}).get("text", "").strip().lower()

                    if message_text:
                        logging.info(f"📩 Message from {sender_id}: {message_text}")

                        # 💬 Respond based on message text
                        if message_text == "hello":
                            send_message(sender_id, "Hey there! 👋")
                        elif message_text == "/help":
                            send_message(sender_id, "Here to help! Try typing 'hello' or '/help'.")
                        else:
                            send_message(sender_id, "I didn’t understand that. Try typing '/help'.")

        return JSONResponse(content={"status": "ok"}, status_code=200)

    except Exception as e:
        logging.error(f"❌ Error handling webhook: {e}")
        return JSONResponse(content={"error": "Something went wrong"}, status_code=500)


# 📤 Function to send a message using Facebook Graph API
def send_message(recipient_id: str, message: str):
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, params=params, json=data, headers=headers)
    if response.status_code != 200:
        logging.error(f"❌ Failed to send message: {response.text}")
    else:
        logging.info(f"✅ Sent message to {recipient_id}: {message}")
