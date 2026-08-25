import gspread
from google.oauth2.service_account import Credentials
from telegram import Bot
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio
import os

TOKEN = os.environ["8907586103:AAH_e1c7NQtSxYgUVOVuFJz3FGaWb2ZO3WM"]

GROUP_ID = -1004385944778

JSON_FILE = "navbatchilik-bot-a1500f896dd8.json"

SHEET_NAME = "navbatchilik"
WORKSHEET_NAME = "Лист1"

SEND_HOUR = 8
SEND_MINUTE = 0

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_file(
    JSON_FILE,
    scopes=SCOPES
)

client = gspread.authorize(credentials)

sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

bot = Bot(token=TOKEN)


async def send_today_duty():
    today = datetime.now(
        ZoneInfo("Asia/Tashkent")
    ).strftime("%d.%m.%Y")

    rows = sheet.get_all_records()

    people = []

    for row in rows:
        sana = str(row.get("Sana", "")).strip()
        navbatchi = str(row.get("Navbatchi", "")).strip()
        telegram = str(row.get("Telegram", "")).strip()

        if sana == today:
            if telegram:
                people.append(f"👤 {navbatchi} — {telegram}")
            else:
                people.append(f"👤 {navbatchi}")

    if people:
        message = (
            f"📅 Bugungi navbatchilar\n"
            f"🗓 {today}\n\n"
            + "\n".join(people)
        )
    else:
        message = (
            f"📅 {today}\n\n"
            "Bugun navbatchi ma'lumotlari topilmadi."
        )

    await bot.send_message(
        chat_id=GROUP_ID,
        text=message
    )

    print("Xabar yuborildi:", today)


async def main():
    print("Bot ishlayapti...")
    print("Har kuni 08:00 da xabar yuboradi.")

    last_sent_date = None

    while True:
        now = datetime.now(
            ZoneInfo("Asia/Tashkent")
        )

        today = now.date()

        # 08:00 ga yetgan bo'lsa va bugun hali yuborilmagan bo'lsa
        if (
            (now.hour > SEND_HOUR or
             (now.hour == SEND_HOUR and now.minute >= SEND_MINUTE))
            and last_sent_date != today
        ):
            try:
                await send_today_duty()
                last_sent_date = today
            except Exception as e:
                print("Xabar yuborishda xatolik:", e)

        await asyncio.sleep(20)


if __name__ == "__main__":
    asyncio.run(main())
