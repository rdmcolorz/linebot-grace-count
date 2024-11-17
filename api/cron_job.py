import os
from linebot import LineBotApi
from api.flex_messages import create_all_counter_message
from api.db import User

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
EVENT_DATA = [
        {'C': '主日', 'D': '禱告聚會', 'H': '小排'},
        {'E': '晨興', 'F': '家聚會', 'G': '家受訪'},
        {'J': '生命讀經', 'K': '天天生命讀經'},
        {'I': '傳福音', 'L': '個人禱告'}
    ]

def send_weekly_notification():
    user = User(None, None, None)
    user_id_list = user.fetch_all_user_ids()
    line_bot_api.multicast(
        user_id_list,
        create_all_counter_message(f'嗨～來週點名囉～', EVENT_DATA, state="")
    )

if __name__ == "__main__":
    print("Triggered cron job")
    send_weekly_notification()