import gspread
from google.oauth2.service_account import Credentials
from telegram import Bot
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio
import os

TOKEN = os.environ["BOT_TOKEN"]

GROUP_ID = -1004385944778

JSON_FILE = "navbatchilik-bot-a1500f896dd8.json"

SHEET_NAME = "navbatchilik"
WORKSHEET_NAME = "Лист1"

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

    print("Xabar yuborildi:", today, flush=True)

async def main():
    # Xabarni bir marta yuboradi va darhol tugaydi.
    # Har kuni soat 08:00 da ishga tushirishni GitHub Actions jadvali bajaradi.
    await send_today_duty()

if __name__ == "__main__":
    asyncio.run(main())
