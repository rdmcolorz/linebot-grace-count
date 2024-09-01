import os
import json
import gspread
from google.oauth2.service_account import Credentials

from flask import current_app

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
cred_json = json.loads(os.getenv("SERVICE_ACC_SECRET"))
creds = Credentials.from_service_account_info(cred_json, scopes=scope)
client = gspread.authorize(creds)

NAME_MAP = {
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
    "Grace Lee": "27",
    "張筱翊": "28",
    "柯星臨": "29",
    "Zera 😊": "30",
    "周佳韻": "31",
    "余其樺": "32",
    "蔡紋綺": "33",
    "楊歆悅": "34",
    "林佳瑩": "35",
    "何繡富": "36",
    "朱珮瑜": "37",
    "李麗仙": "38",
    "王麗美": "39",
    "秦孝芬": "40",
    "魏廷妤": "41",
    "恩榮": "42",
    "曾慕華": "43"
}


def update_gsheet_checkbox(name, event, attend):
    sheet_key = '1wMN8njXEchf9-GedPcsz0eKCvJpYUBxaHPUelBdamKQ'
    sheet_name = 'grace'

    name_id = NAME_MAP.get(name)
    if name_id:
        try:
            spreadsheet = client.open_by_key(sheet_key)
            sheet = spreadsheet.worksheet(sheet_name)
            sheet.update_acell(f"{event}{name_id}", attend)
            current_app.logger.info(f"gsheet updated at {event}{name_id}, value: {attend}")
        except Exception as e:
            current_app.logger.error(e)
    else:
        current_app.logger.info(f'{name} doesnt have name_id, please add to mapping')


def update_gsheet_checkbox_batch(name, state):
    sheet_key = '1wMN8njXEchf9-GedPcsz0eKCvJpYUBxaHPUelBdamKQ'
    sheet_name = 'grace'

    name_id = NAME_MAP.get(name)
    if name_id:
        try:
            update_values = []
            for e in 'CDEFGHIJKL':
                if e in state:
                    update_values.append(True)
                else:
                    update_values.append(False)
            print(update_values)
            spreadsheet = client.open_by_key(sheet_key)
            sheet = spreadsheet.worksheet(sheet_name)
            sheet.update(f"C{name_id}:L{name_id}", [update_values])
            current_app.logger.info(f"gsheet updated at {name_id}, value: {update_values}")
        except Exception as e:
            print('error what')
            current_app.logger.error(e)
    else:
        current_app.logger.info(f'{name} doesnt have name_id, please add to mapping')