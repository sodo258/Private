import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ================= 設定區 =================

# 1. 你的 LINE 鑰匙 (阿華專用暴力填入版，確保不會錯)
line_bot_api = LineBotApi('X8GnvO9JUVfypVoeIqgrSP+ChOScdKKloZe0wwfnJdL8C0LgHFqLSsB1TMYacx7xzFpL/R9lLA7LkARFuK79y6/ofObPJiqFpJj94C1Knk1aoERNdHh+XVvGnV2scudJ+D1UeU/bZOCeAxe7/iH6DgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('783cc9d3091b87f45298bc67e383b9ea')

# 2. Google 試算表設定 (你剛剛填的 ID)
SPREADSHEET_ID = '1G57LlXcUnbGTAPQcg-dHlX2_hrO19a9WTEXRWvLee1s'

# 設定 Google 權限範圍
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# 嘗試連線到 Google Sheets
try:
    # 這裡一定要讀取 Render 環境變數，不然程式碼會太亂
    json_creds = os.environ.get('GOOGLE_JSON')
    if not json_creds:
        print("❌ 錯誤：找不到 GOOGLE_JSON 環境變數！")
    else:
        creds_dict = json.loads(json_creds)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        print("Google Sheet 連線成功！")
except Exception as e:
    print(f"Google Sheet 連線失敗: {e}")

# =========================================

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
    return "Friday Mahjong Bot is Running!"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.strip()
    
    # 指令觸發檢查
    if msg.startswith('#') or msg.lower().startswith('friday'):
        content = msg.replace('#', '').replace('Friday', '').replace('friday', '').strip()
        parts = content.split()
        
        if len(parts) >= 2:
            name = parts[0]
            score = parts[1]
            try:
                # 寫入試算表
                sheet.append_row([name, score])
                reply_text = f"✅ 紀錄成功！\n{name}: {score}"
            except Exception as e:
                reply_text = f"❌ 寫入失敗！\n可能是 GOOGLE_JSON 沒設定好，或是機器人沒被加入試算表共用。\n錯誤訊息：{e}"
        else:
            reply_text = "❓ 格式錯囉！\n請輸入：#名字 分數\n例如：#阿華 300"
            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
