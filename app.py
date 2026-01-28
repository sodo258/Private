import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# =========== 暴力測試區：直接填入你的鑰匙 ===========

# 你的 Token (長的那串)
line_bot_api = LineBotApi('X8GnvO9JUVfypVoeIqgrSP+ChOScdKKloZe0wwfnJdL8C0LgHFqLSsB1TMYacx7xzFpL/R9lLA7LkARFuK79y6/ofObPJiqFpJj94C1Knk1aoERNdHh+XVvGnV2scudJ+D1UeU/bZOCeAxe7/iH6DgdB04t89/1O/w1cDnyilFU=')

# 你的 Secret (短的那串)
handler = WebhookHandler('783cc9d3091b87f45298bc67e383b9ea')

# =================================================

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 如果這裡報錯，代表簽名不對
        print("Invalid Signature Error!")
        abort(400)
    return 'OK'

@app.route("/")
def home():
    return "Friday is hardcoded!"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"Friday 收到：{msg}")
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
