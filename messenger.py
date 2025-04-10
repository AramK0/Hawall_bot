from fastapi import FastAPI, Request
import requests

app = FastAPI()

VERIFY_TOKEN = "your_verify_token"  # Token to verify Facebook webhook
PAGE_ACCESS_TOKEN = "your_page_access_token"  # Token for sending messages via Facebook

@app.get("/webhook")
async def verify_webhook(request: Request, hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    """
    Facebook requires a GET request to verify the webhook URL during setup.
    If the tokens match, the webhook is successfully verified.
    """
    if hub_verify_token == VERIFY_TOKEN:
        return hub_challenge  # Facebook will match the challenge and verify the webhook.
    return "Verification failed", 403

@app.post("/webhook")
async def receive_message(request: Request):
    """
    This POST endpoint will be called by Facebook Messenger whenever a new event occurs.
    This includes messages, button clicks, etc.
    """
    data = await request.json()
    # Loop through the events (messages or other events) sent by Facebook
    for entry in data["entry"]:
        for message in entry["messaging"]:
            sender_id = message["sender"]["id"]
            if "message" in message:
                text = message["message"]["text"]
                send_message(sender_id, text)  # Respond back with the same message (for now)

    return "OK"

def send_message(recipient_id, text):
    """Function to send a reply to the user on Facebook Messenger"""
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.status_code, response.text)

