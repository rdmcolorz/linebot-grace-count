import os

from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, \
    TextSendMessage, PostbackEvent, FollowEvent
from api.flex_messages import create_all_counter_message, create_event_flex_message
from api.gsheet import update_gsheet_checkbox
from api.db import User

# from dotenv import load_dotenv
# load_dotenv()


line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

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

@line_handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    name = profile.display_name
    user = User(user_id, None, name)
    user.add_user()
    welcome_message = TextSendMessage(
        text='歡迎加入博愛區的點名！\n輸入 點名 就可以開始這週的點名囉！'
    )
    line_bot_api.reply_message(event.reply_token, welcome_message)


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
    if event.message.text == "點名":
        user_id = event.source.user_id
        profile = line_bot_api.get_profile(user_id)
        name = profile.display_name
        user = User(user_id, None, name)
        user.add_user()
        events = [
            {'C': '主日', 'D': '禱告聚會', 'E': '家聚會'},
            {'F': '家受訪', 'G': '小排', 'H': '晨興'},
            {'I': '傳福音', 'J': '生命讀經'},
            {'K': '天天生命讀經', 'L': '個人禱告'}
        ]
        line_bot_api.reply_message(
            event.reply_token,
            create_all_counter_message('週點名', events)
        )
        return
    if event.message.text == "check in":
        events = [
            {'C': 'Lords Day', 'D': 'Prayer Meeting', 'E': '家聚會'},
            {'F': '家受訪', 'G': 'Home meeting', 'H': 'Morning revival'},
            {'I': '', 'J': '生命讀經'},
            {'K': '天天生命讀經', 'L': 'Personal Prayers'}
        ]
        line_bot_api.reply_message(
            event.reply_token,
            create_all_counter_message('Weekly Check-in', events)
        )
        return
    # if event.message.text == '通知':
    #     user_id = event.source.user_id
    #     profile = line_bot_api.get_profile(user_id)
    #     name = profile.display_name
    #     user = User(user_id, None, name)

    #     if name == '楊光宇':
    #         user_id_list = user.fetch_all_user_ids()
    #         line_bot_api.multicast(
    #             user_id_list,
    #             create_all_counter_message()
    #         )


@line_handler.add(PostbackEvent)
def handle_postback(event):
    # Get data sent with postback
    data = event.postback.data
    group_id = getattr(event.source, 'group_id', None)
    user_id = event.source.user_id

    parsed_data = parse_data(data)
    attend = parsed_data.get('attend')
    event_id = parsed_data['event']

    event_map = {
        "C": "主日聚會",
        "D": "禱告聚會",
        'E': '家聚會',
        'F': '家受訪',
        "G": "小排聚會",
        'H': '晨興',
        'I': '傳福音',
        'J': '生命讀經',
        'K': '天天生命讀經',
        'L': '個人禱告'
    }

    if group_id:
        group_id = event.source.group_id
        profile = line_bot_api.get_group_member_profile(group_id, user_id)
    else:
        profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name
    update_gsheet_checkbox(user_name, event_id, attend)
    if attend == 'TRUE':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{user_name}：{event_map[event_id]} 簽到了～")
        )

if __name__ == "__main__":
    app.run()
