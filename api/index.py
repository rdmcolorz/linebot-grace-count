import os

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, \
    TextSendMessage, PostbackEvent
from api.flex_messages import create_all_counter_message, create_event_flex_message
from api.gsheet import update_gsheet_checkbox

# from dotenv import load_dotenv
# load_dotenv()


line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)

def parse_data(input_string):
    pairs = input_string.split('&')
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
    if event.message.type != "text":
        return

    if event.message.text == "點名 主日":
        line_bot_api.reply_message(
            event.reply_token,
            create_event_flex_message("主日聚會", 'C')
        )
        return
    if event.message.text == "點名 小排":
        line_bot_api.reply_message(
            event.reply_token,
            create_event_flex_message("週三/四 小排聚會", 'D')
        )
        return
    if event.message.text == "點名 禱告聚會":
        line_bot_api.reply_message(
            event.reply_token,
            create_event_flex_message("週二 禱告聚會", 'G')
        )
        return
    if event.message.text == "全點名":
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

    if group_id:
        profile = line_bot_api.get_group_member_profile(group_id, user_id)
    else:
        profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name
    update_gsheet_checkbox(user_name, event_id, attend)
    if attend == 'TRUE':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{user_name}來到{event_map[event_id]}了～")
        )

if __name__ == "__main__":
    app.run()
