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
# 1. 你的 LINE 鑰匙 (建議之後也搬到 Render 環境變數，目前先保留你的暴力法或用變數)
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN')) 
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

# 2. Google 試算表設定
SPREADSHEET_ID = '1G57LlXcUnbGTAPQcg-dHlX2_hrO19a9WTEXRWvLee1s'  # <--- 請記得改這裡！！！

# 設定 Google 權限範圍
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# 嘗試連線到 Google Sheets
try:
    # 從 Render 環境變數讀取 JSON 內容
    json_creds = os.environ.get('GOOGLE_JSON')
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
    msg = event.message.text.strip() # 去除前後空白
    
    # 判斷指令：如果是 # 開頭，或是直接叫 Friday
    # 範例輸入： #阿華 300
    
    if msg.startswith('#') or msg.lower().startswith('friday'):
        
        # 1. 處理字串，把前面的符號拿掉
        content = msg.replace('#', '').replace('Friday', '').replace('friday', '').strip()
        
        # 2. 切割字串，預期會拿到 [名字, 分數]
        # 例如 "阿華 300" ->parts[0]=阿華, parts[1]=300
        parts = content.split()
        
        if len(parts) >= 2:
            name = parts[0]
            score = parts[1]
            
            # 3. 寫入 Google 試算表
            try:
                # 寫入一行：[名字, 分數] (你可以自己加日期)
                sheet.append_row([name, score])
                reply_text = f"✅ 紀錄成功！\n{name}: {score}"
            except Exception as e:
                reply_text = f"❌ 寫入失敗，請檢查權限或 ID。\n錯誤：{str(e)}"
        else:
            reply_text = "❓ 格式看不懂喔。\n請輸入：#名字 分數\n例如：#阿華 300"
            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
