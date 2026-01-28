import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ================= 填入你的鑰匙 =================
# 建議：為了安全，之後我們會教你用「環境變數」藏起來
# 但現在為了先跑通，你可以先直接貼上
line_bot_api = LineBotApi('你的長長那一串_Channel_Access_Token')
handler = WebhookHandler('你的短短那一串_Channel_Secret')
# ===============================================

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route("/")
def home():
    return "Friday is Online!"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    # 鸚鵡學舌功能
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"Friday 收到：{user_msg}")
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)