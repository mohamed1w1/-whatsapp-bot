from flask import Flask, request, jsonify
import requests, json

app = Flask(__name__)

TOKEN = "ACCESS_TOKEN_BTATAK"
PHONE_ID = "993956793812385"
VERIFY_TOKEN = "mybot123"

with open("qa.json", "r", encoding="utf-8") as f:
    QA = json.load(f)

def find_answer(user_msg):
    user_msg = user_msg.lower().strip()
    for item in QA:
        for keyword in item["keywords"]:
            if keyword in user_msg:
                return item["answer"]
    return "شكراً لتواصلك! هرد عليك في أقرب وقت 🙏"

def send_whatsapp(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = msg["from"]
        text = msg["text"]["body"]
        answer = find_answer(text)
        send_whatsapp(from_number, answer)
    except:
        pass
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
