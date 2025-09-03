import os
import re
import json
import datetime as dt
from typing import Optional, Tuple, Dict, Any

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore


CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _get_timezone(timezone_str: str) -> Optional[Any]:
    if ZoneInfo is None:
        return None
    try:
        return ZoneInfo(timezone_str)
    except Exception:
        return None


def _build_calendar_service():
    cred_json_str = os.getenv("SERVICE_ACC_SECRET")
    if not cred_json_str:
        raise RuntimeError("SERVICE_ACC_SECRET is not set in environment.")
    cred_json = json.loads(cred_json_str)
    creds = Credentials.from_service_account_info(cred_json, scopes=CALENDAR_SCOPES)
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    return service


_calendar_service = None


def get_calendar_service():
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = _build_calendar_service()
    return _calendar_service


def _extract_date(text: str, now: Optional[dt.datetime]) -> Tuple[Optional[dt.date], Optional[Tuple[int, int, Optional[str]]]]:
    if now is None:
        now = dt.datetime.now()

    m = re.search(r"(\d{4})[\-/](\d{1,2})[\-/](\d{1,2})", text)
    if m:
        year, month, day = map(int, m.groups())
        date_obj = dt.date(year, month, day)
        return date_obj, _extract_time(text)

    m = re.search(r"(\d{1,2})[\-/](\d{1,2})(?!\d)", text)
    if m:
        month, day = map(int, m.groups())
        year = now.year
        date_obj = dt.date(year, month, day)
        return date_obj, _extract_time(text)

    m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日", text)
    if m:
        month, day = map(int, m.groups())
        year = now.year
        date_obj = dt.date(year, month, day)
        return date_obj, _extract_time(text)

    return None, None


def _extract_time(text: str) -> Optional[Tuple[int, int, Optional[str]]]:
    m = re.search(r"(上午|下午|AM|PM)?\s*(\d{1,2})[:：](\d{2})", text, re.IGNORECASE)
    if m:
        ampm = m.group(1)
        hour = int(m.group(2))
        minute = int(m.group(3))
        return hour, minute, ampm

    m = re.search(r"(上午|下午)?\s*(\d{1,2})\s*(?:點|時)\s*(?:(\d{1,2})\s*分?)?", text)
    if m:
        ampm = m.group(1)
        hour = int(m.group(2))
        minute = int(m.group(3)) if m.group(3) else 0
        return hour, minute, ampm

    return None


def _apply_ampm(hour: int, ampm: Optional[str]) -> int:
    if not ampm:
        return hour
    ampm = ampm.upper() if isinstance(ampm, str) else ampm
    if ampm in ["PM", "下午"] and hour < 12:
        return hour + 12
    if ampm in ["AM", "上午"] and hour == 12:
        return 0
    return hour


def parse_event_text(text: str, timezone_str: str = "Asia/Taipei", now: Optional[dt.datetime] = None) -> Optional[Dict[str, Any]]:
    if not text or len(text) < 4:
        return None

    if now is None:
        now = dt.datetime.now()

    date_obj, time_tuple = _extract_date(text, now)
    if not date_obj:
        return None

    text_clean = re.sub(r"(\d{4})[\-/](\d{1,2})[\-/](\d{1,2})", " ", text)
    text_clean = re.sub(r"(\d{1,2})[\-/](\d{1,2})(?!\d)", " ", text_clean)
    text_clean = re.sub(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日", " ", text_clean)
    text_clean = re.sub(r"(上午|下午|AM|PM)?\s*(\d{1,2})[:：](\d{2})", " ", text_clean, flags=re.IGNORECASE)
    text_clean = re.sub(r"(上午|下午)?\s*(\d{1,2})\s*(?:點|時)\s*(?:(\d{1,2})\s*分?)?", " ", text_clean)
    title = re.sub(r"\s+", " ", text_clean).strip()
    if not title:
        title = "未命名活動"

    tzinfo = _get_timezone(timezone_str)

    if time_tuple:
        hour, minute, ampm = time_tuple
        hour = _apply_ampm(hour, ampm)
        start_dt = dt.datetime(date_obj.year, date_obj.month, date_obj.day, hour, minute)
        end_dt = start_dt + dt.timedelta(hours=1)
        if tzinfo is not None:
            start_dt = start_dt.replace(tzinfo=tzinfo)
            end_dt = end_dt.replace(tzinfo=tzinfo)
        return {
            "title": title,
            "all_day": False,
            "start_dt": start_dt,
            "end_dt": end_dt,
            "date": None,
        }
    else:
        return {
            "title": title,
            "all_day": True,
            "start_dt": None,
            "end_dt": None,
            "date": date_obj,
        }


def create_calendar_event(
    summary: str,
    calendar_id: Optional[str] = None,
    start_dt: Optional[dt.datetime] = None,
    end_dt: Optional[dt.datetime] = None,
    date: Optional[dt.date] = None,
    timezone_str: str = "Asia/Taipei",
    description: Optional[str] = None,
    location: Optional[str] = None,
) -> Dict[str, Any]:
    if calendar_id is None:
        calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

    body: Dict[str, Any] = {
        "summary": summary,
    }
    if description:
        body["description"] = description
    if location:
        body["location"] = location

    if date is not None:
        body["start"] = {"date": date.isoformat(), "timeZone": timezone_str}
        body["end"] = {"date": (date + dt.timedelta(days=1)).isoformat(), "timeZone": timezone_str}
    else:
        if start_dt is None or end_dt is None:
            raise ValueError("start_dt and end_dt must be provided for timed events")
        body["start"] = {"dateTime": start_dt.isoformat(), "timeZone": timezone_str}
        body["end"] = {"dateTime": end_dt.isoformat(), "timeZone": timezone_str}

    service = get_calendar_service()
    event = service.events().insert(calendarId=calendar_id, body=body).execute()
    return event


