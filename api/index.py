import os
import json
import gspread
from google.oauth2.service_account import Credentials

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, \
    TextSendMessage, FlexSendMessage, BubbleContainer, \
    BoxComponent, TextComponent, ButtonComponent, \
    PostbackAction, PostbackEvent
from api.flex_messages import create_all_counter_message

# from dotenv import load_dotenv
# load_dotenv()

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

cred_json = json.loads(os.getenv("SERVICE_ACC_SECRET"))

creds = Credentials.from_service_account_info(cred_json, scopes=scope)
client = gspread.authorize(creds)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)

def create_flex_message(event, event_id):
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='xl',
            contents=[
                TextComponent(text=event, weight='bold', size='xl'),
                ButtonComponent(
                    action=PostbackAction(
                        label='我來了！',
                        data=f'event:{event_id}&attend:TRUE',
                        # display_text='已簽到！',
                        size='lg'
                    ),
                    style='primary'
                ),
                ButtonComponent(
                    action=PostbackAction(
                        label='我下次再來～',
                        data=f'event:{event_id}&attend:FALSE',
                        # display_text='下次來～！',
                        size='lg'
                    ),
                    style='secondary'
                )
            ]
        )
    )
    flex_message = FlexSendMessage(
        alt_text='恩典點名', contents=bubble
    )
    return flex_message


def parse_data(input_string):
    # Split the string by '&' to get key-value pairs
    pairs = input_string.split('&')

    # Create a dictionary from the key-value pairs
    result = {}
    for pair in pairs:
        key, value = pair.split(':')
        result[key] = value
    return result


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

    if event.message.text == "點名 主日":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            create_flex_message("主日聚會", 'C')
        )
        return
    if event.message.text == "點名 小排":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            create_flex_message("週三/四 小排聚會", 'D')
        )
        return
    if event.message.text == "點名 禱告聚會":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            create_flex_message("週二 禱告聚會", 'G')
        )
        return
    if event.message.text == "全點名":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            create_all_counter_message()
        )
        return


@line_handler.add(PostbackEvent)
def handle_postback(event):
    # Get data sent with postback
    data = event.postback.data
    group_id = event.source.group_id
    user_id = event.source.user_id

    parsed_data = parse_data(data)
    attend = parsed_data.get('attend')
    event_id = parsed_data['event']

    event_map = {
        "C": "主日聚會",
        "D": "禱告聚會",
        "G": "小排聚會"
    }

    profile = line_bot_api.get_group_member_profile(group_id, user_id)
    user_name = profile.display_name
    update_gsheet_checkbox(user_name, event_id, attend)
    if attend == 'TRUE':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{user_name}來到{event_map[event_id]}了～")
        )


def update_gsheet_checkbox(name, event, attend):
    sheet_key = '1wMN8njXEchf9-GedPcsz0eKCvJpYUBxaHPUelBdamKQ'
    sheet_name = 'grace'
    name_map = {
        "daniel": "2",
        "柯建伸": "3",
        "David Lee": "4",
        "曾木宣": "5",
        "楊光宇": "6",
        "李成新": "7",
        "王志均": "8",
        "王仲會": "9",
        "華國": "10",
        "施明隴": "11",
        "李其翰": "12",
        "張孝全": "13",
        "李國言": "15",
        "李宜耕": "16",
        "蔡政達": "17",
        "Grace Lee": "26",
        "張筱翊": "27",
        "柯星臨": "28",
        "Zera 😊": "29",
        "周佳韻": "30",
        "余其樺": "31",
        "蔡紋綺": "32",
        "楊歆悅": "33",
        "林佳瑩": "34",
        "何繡富": "35",
        "朱珮瑜": "36",
        "李麗仙": "37",
        "王麗美": "38",
        "秦孝芬": "39",
        "魏廷妤": "40",
        "恩榮": "41",
        "曾慕華": "42"
    }
    name_id = name_map.get(name)
    if name_id:
        spreadsheet = client.open_by_key(sheet_key)
        sheet = spreadsheet.worksheet(sheet_name)
        sheet.update_acell(f"{event}{name_id}", attend)
        app.logger.info(f"gsheet updated at {event}{name_id}, value: {attend}")
    else:
        app.logger.info(f'{name} doesnt have name_id, please add to mapping')

if __name__ == "__main__":
    app.run()
