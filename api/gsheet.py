import os
import json
import gspread
from google.oauth2.service_account import Credentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
cred_json = json.loads(os.getenv("SERVICE_ACC_SECRET"))
creds = Credentials.from_service_account_info(cred_json, scopes=scope)
client = gspread.authorize(creds)


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
        app.logger.error(f"gsheet updated at {event}{name_id}, value: {attend}")
    else:
        app.logger.info(f'{name} doesnt have name_id, please add to mapping')