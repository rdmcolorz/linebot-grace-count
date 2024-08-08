import json
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, BubbleContainer, BoxComponent, TextComponent, ButtonComponent, URIAction


import os

load_dotenv()
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

cred_json = json.loads(os.getenv("SERVICE_ACC_SECRET"))

creds = Credentials.from_service_account_info(cred_json, scopes=scope)
client = gspread.authorize(creds)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)

def create_flex_message(type):
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text=type, weight='bold', size='xl'),
                ButtonComponent(
                    action=URIAction(label='Go to Website', uri='https://google.com')
                )
            ]
        )
    )
    flex_message = FlexSendMessage(alt_text='This is a Flex Message', contents=bubble)
    return flex_message

# domain root
@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    if event.message.type != "text":
        return

    if event.message.text == "點名":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            create_flex_message("prayer_meeting")
        )
        return

    # if working_status:
    #     chatgpt.add_msg(f"HUMAN:{event.message.text}?\n")
    #     reply_msg = chatgpt.get_response().replace("AI:", "", 1)
    #     chatgpt.add_msg(f"AI:{reply_msg}\n")
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=reply_msg))


if __name__ == "__main__":
    # spreadsheet = client.open_by_key('1wMN8njXEchf9-GedPcsz0eKCvJpYUBxaHPUelBdamKQ')
    # sheet = spreadsheet.worksheet('test')
    # sheet.update('A1:B2', [[1, 2], [3, 4]])
    app.run()
