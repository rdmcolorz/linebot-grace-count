import os
import datetime
from flask import Flask, request, abort, jsonify

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, \
    TextSendMessage, PostbackEvent, FollowEvent
from api.flex_messages import create_all_counter_message
from api.gsheet import update_gsheet_checkbox_batch
from api.db import User

# from dotenv import load_dotenv
# load_dotenv()


line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

EVENT_DATA = [
        {'C': '主日', 'D': '禱告聚會', 'H': '小排'},
        {'E': '晨興', 'F': '家聚會', 'G': '家受訪'},
        {'J': '生命讀經', 'K': '天天生命讀經'},
        {'I': '傳福音', 'L': '個人禱告'}
    ]

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
    
    # TODO: reply with instructions if message can't be parsed.
    if event.message.type == "text" and event.message.text not in ["點名", "通知我", "通知"]:
        welcome_message = TextSendMessage(
            text='歡迎加入博愛區的點名！\n輸入 點名 就可以開始這週的點名囉！'
        )
        line_bot_api.reply_message(event.reply_token, welcome_message)
        return

    if event.message.text == "點名":
        line_bot_api.reply_message(
            event.reply_token,
            create_all_counter_message('週點名', EVENT_DATA, state="")
        )
        print(datetime.datetime.now(), "replied message")
        return

    if event.message.text == "通知我":
        user_id = event.source.user_id
        profile = line_bot_api.get_profile(user_id)
        name = profile.display_name
        user = User(user_id, None, name)
        user.add_user()
        message = TextSendMessage(
            text=f'{name} 已加入通知清單！'
        )
        line_bot_api.reply_message(event.reply_token, message)


    # TODO: Add english verison
    # if event.message.text == "check in":
    #     events = [
    #         {'C': 'Lords Day', 'D': 'Prayer Meeting', 'E': '家聚會'},
    #         {'F': '家受訪', 'G': 'Home meeting', 'H': 'Morning revival'},
    #         {'I': '', 'J': '生命讀經'},
    #         {'K': '天天生命讀經', 'L': 'Personal Prayers'}
    #     ]
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         create_all_counter_message('Weekly Check-in', events)
    #     )
    #     return

    # TODO: Add ability to trigger push notifications to all friends.
    # if event.message.text == '通知':
    #     user_id = event.source.user_id
    #     profile = line_bot_api.get_profile(user_id)
    #     name = profile.display_name
    #     user = User(user_id, None, name)

    #     if name == '楊光宇':
    #         user_id_list = user.fetch_all_user_ids()
    #         line_bot_api.multicast(
    #             user_id_list,
    #             create_all_counter_message(f'嗨～來週點名囉～', EVENT_DATA, state="")
    #         )

@app.route("/api/weekly", methods=['GET'])
def weekly_job_handler():
    print("weekly triggered")
    user = User(None, None, None)
    user_id_list = user.fetch_all_user_ids()
    line_bot_api.multicast(
        user_id_list,
        create_all_counter_message(f'嗨～來週點名囉～', EVENT_DATA, state="")
    )
    return jsonify({"message": "Cron job executed successfully!"}), 200

@line_handler.add(PostbackEvent)
def handle_postback(event):
    # Get data sent with postback
    data = event.postback.data
    group_id = getattr(event.source, 'group_id', None)
    user_id = event.source.user_id
    parsed_data = parse_data(data)
    action_type = parsed_data.get('action')

    if action_type == 'r':
        handle_gsheet_record(event, parsed_data, user_id, group_id)
    elif action_type == 'n':
        next_question(event, parsed_data)


def next_question(event, parsed_data):
    state = parsed_data.get('state')
    line_bot_api.reply_message(
        event.reply_token,
        create_all_counter_message('週點名', EVENT_DATA, state)
    )
    return


def handle_gsheet_record(event, parsed_data, user_id, group_id):
    state = parsed_data.get('state')

    event_map = {
        "C": "主日聚會",
        "D": "禱告聚會",
        'E': '晨興',
        'F': '家出訪',
        "G": "家受訪",
        'H': '小排',
        'I': '傳福音',
        'J': '生命讀經',
        'K': '天天生命讀經',
        'L': '個人禱告'
    }

    # if group_id:
    #     group_id = event.source.group_id
    #     profile = line_bot_api.get_group_member_profile(group_id, user_id)
    # else:
    profile = line_bot_api.get_profile(user_id)

    user_name = profile.display_name
    update_gsheet_checkbox_batch(user_name, state)
    checked_events = ', '.join([event_map[id] for id in state])
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"{user_name} 於 {checked_events} 簽到了～")
    )


if __name__ == "__main__":
    app.run()
