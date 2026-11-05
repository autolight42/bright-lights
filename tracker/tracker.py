import asyncio
import requests
import os
import threading
from datetime import datetime, timezone, timedelta
from flask import Flask
from telethon import TelegramClient
from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently

# --- ВАШИ ДАННЫЕ ---
API_ID = 32490814          
API_HASH = "b4fd31009f703c16e91bb09cc9e8be8f"       
TARGET_USERNAME = "@rykoatka3" 
CHECK_INTERVAL = 10  

BOT_TOKEN = "9287965458:AAE9SIsstSvN_LWa6BFNokPwc6BQ-KsY4DA" 
YOUR_CHAT_ID = 7901480463  
# -------------------

TZ_OFFSET = timezone(timedelta(hours=7)) 

def get_time_now():
    return datetime.now(TZ_OFFSET).strftime('%d.%m.%Y %H:%M:%S')

def send_tg_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": YOUR_CHAT_ID, "text": text}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"Не удалось отправить уведомление: {e}")

# --- TELEGRAM TRACKER ---
client = TelegramClient("session_tracker", API_ID, API_HASH)

async def tracker_loop():
    await client.start()
    print(f"Слежка за {TARGET_USERNAME} началась...")
    send_tg_message(f"✅ Слежка за {TARGET_USERNAME} успешно запущена на сервере!")

    last_status = None

    while True:
        try:
            user = await client.get_entity(TARGET_USERNAME)
            status = user.status

            if isinstance(status, UserStatusOnline):
                current = "online"
                if last_status != current:
                    msg = f"🟢 [{get_time_now()}] {TARGET_USERNAME} В СЕТИ!"
                    print(msg)
                    send_tg_message(msg)
                
            elif isinstance(status, UserStatusOffline):
                current = "offline"
                if last_status != current:
                    raw_dt = status.was_online
                    clean_dt = datetime(raw_dt.year, raw_dt.month, raw_dt.day, raw_dt.hour, raw_dt.minute, raw_dt.second)
                    final_dt = clean_dt + timedelta(hours=7)
                    was_online = final_dt.strftime('%d.%m.%Y %H:%M:%S')
                    
                    msg = f"🔴 [{get_time_now()}] {TARGET_USERNAME} ВЫШЕЛ. Был в сети: {was_online}"
                    print(msg)
                    send_tg_message(msg)
                
            elif isinstance(status, UserStatusRecently):
                current = "recently"
                if last_status != current:
                    msg = f"🟡 [{get_time_now()}] {TARGET_USERNAME}: недавно"
                    print(msg)
            else:
                current = "hidden"
                if last_status != current:
                    msg = f"⚪ [{get_time_now()}] {TARGET_USERNAME}: статус скрыт"
                    print(msg)

            last_status = current
        except Exception as e:
            print(f"Ошибка: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    # UptimeRobot будет открывать эту страницу, чтобы сервер не засыпал
    return "Tracker is running!"

def run_flask():
    # Render сам назначит порт, либо используем 8080 по умолчанию
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Запускаем веб-сервер в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Запускаем слежку
    with client:
        client.loop.run_until_complete(tracker_loop())
