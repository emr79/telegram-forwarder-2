import asyncio
import logging
import os
from telethon import TelegramClient
from telethon.tl.patched import MessageService
from telethon.errors.rpcerrorlist import FloodWaitError

# --- الإعدادات (بياناتك) ---
API_ID = 37455278
API_HASH = '5432caa3c48372d0992142a8ed6dbef4'
SOURCE_CHAT = 'lovekotob'
TO_CHAT = 'akooaaj'

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- وظائف حفظ التقدم ---
def get_last_id():
    if os.path.exists('progress.txt'):
        with open('progress.txt', 'r') as f:
            return int(f.read().strip())
    return 0

def save_last_id(current_id):
    with open('progress.txt', 'w') as f:
        f.write(str(current_id))

async def forward_job():
    # استرجاع آخر نقطة توقف
    last_saved_id = get_last_id()
    
    # عدادات الاستراحة المتغيرة
    msg_counter = 0
    sleep_minutes = 30 
    
    session = 'original_style_session'

    async with TelegramClient(session, API_ID, API_HASH) as client:
        logging.info(f"🚀 بدء النقل من الرسالة رقم: {last_saved_id}")

        async for message in client.iter_messages(SOURCE_CHAT, reverse=True, offset_id=last_saved_id):
            if isinstance(message, MessageService):
                continue
            
            try:
                # المحاولة الأصلية للإرسال
                await client.send_message(TO_CHAT, message)
                
                # حفظ الرقم فوراً لضمان عدم التكرار عند انقطاع النت
                save_last_id(message.id)
                msg_counter += 1
                
                logging.info(f"✅ تم نقل: {message.id} | العداد: {msg_counter}/1000")

                # نظام الاستراحة المتغيرة (30, 35, 40...60)
                if msg_counter >= 1000:
                    logging.info(f"☕ استراحة مجدولة لمدة {sleep_minutes} دقيقة...")
                    await asyncio.sleep(sleep_minutes * 60)
                    
                    msg_counter = 0
                    sleep_minutes += 5
                    if sleep_minutes > 60:
                        sleep_minutes = 30
                else:
                    # تأخير بسيط جداً (ثانية واحدة) لضمان الاستقرار
                    await asyncio.sleep(1)

            except FloodWaitError as fwe:
                # إذا طلب تيليجرام التوقف، يتوقف السكريبت المدة المطلوبة ثم يكمل تلقائياً
                logging.warning(f"⏳ قيود تيليجرام: انتظار {fwe.seconds} ثانية...")
                await asyncio.sleep(fwe.seconds)
                
            except Exception as e:
                # في حال حدوث أي خطأ (فشل في رسالة، انقطاع نت)، يتجاوزها ويكمل ولا يتوقف
                logging.error(f"❌ خطأ في الرسالة {message.id}: {e}")
                logging.info("محاولة التجاوز والاستمرار في الرسالة التالية...")
                await asyncio.sleep(5) # انتظار بسيط قبل المحاولة التالية
                continue

if __name__ == "__main__":
    try:
        asyncio.run(forward_job())
    except KeyboardInterrupt:
        logging.info("🛑 تم إيقاف البرنامج يدوياً.")
