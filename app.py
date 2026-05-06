from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WHATSAPP_TOKEN = "ACCESS_TOKEN_BTATAK"
PHONE_ID = "993956793812385"
VERIFY_TOKEN = "mybot123"
GEMINI_KEY = AIzaSyCQXXcZNaw7Uc-F5Uw-fRFWrybmFJ8JstM

SYSTEM_PROMPT = """أنت مساعد خدمة عملاء لمتجر VOX ME للجيمينج.

معلومات المتجر:
- الموقع: https://voxmeshop.com
- واتساب: 01080046634
- المنتجات: كيبوردات ميكانيكية، ماوسات جيمينج، هيدسيتس، ماوس باد

الدفع: كاش عند الاستلام أو تحويل واتساب. قريباً: InstaPay وفودافون كاش
الشحن: 70-100 جنيه، 5-7 أيام، أيام الأحد والاثنين والأربعاء والخميس
الاستبدال: خلال 7 أيام، المنتج جديد لم يستخدم، مع الصندوق والملحقات
الإرجاع: غير متوفر
الضمان: 6 أشهر لسنة حسب المنتج

قواعد الرد:
- ردود قصيرة ومفيدة
- ابدأ بمرحبا أو السلام عليكم
- استخدم إيموجي باعتدال
- المشاكل التقنية والأسئلة الصعبة: حول لـ 01080046634
- لو مش عارف الإجابة: قول تواصل معنا على 01080046634"""

def ask_gemini(user_message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT + "\n\nالعميل: " + user_message}
                ]
            }
        ],
        "generationConfig": {"maxOutputTokens": 300}
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]

def send_whatsapp(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
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
        if msg["type"] != "text":
            return jsonify({"status": "ok"})
        from_number = msg["from"]
        text = msg["text"]["body"]
        reply = ask_gemini(text)
        send_whatsapp(from_number, reply)
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
