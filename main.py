import asyncio
import logging
import os
import sys
from telethon import TelegramClient
from telethon.tl.patched import MessageService
from telethon.errors.rpcerrorlist import FloodWaitError, AuthKeyError, PhoneNumberInvalidError
from telethon.sessions import StringSession

# --- الإعدادات (بياناتك) ---
API_ID = 37455278
API_HASH = '5432caa3c48372d0992142a8ed6dbef4'
SOURCE_CHAT = 'lovekotob'
TO_CHAT = 'akooaaj'

# --- رقم هاتفك مباشرة في الكود ---
PHONE_NUMBER = '+9647838978624'  # ⬅️ رقمك هنا
STRING_SESSION = '1ApWapzMBuweUVYUyz4xfSm4lVLJK-ny42-VqwDD4FwKjAYTy91_agD_N1gj9G0t6d3Rp3JRr6akSqL7dgLGsTMhPlKHBLui87-C3phwPp6AvDxWdMXsFzAxo8V-W_nRfulVGfhFWFEQV22JkmH609-7zxdmkQ5EfQ8DBiJRx9wDYaZ-gS_Ef607PTggE44_v8_OfI-eWZtZA3h3Pdv_dUQB5lxQNw_DFK8qz_Kv1oDzkUQq6CLAgFOItHNMgKHMUfa6NjE403VLk27CsHyGpRF-Yg0AK7P8ts7NVpqDpWjJyE6zIAaUDx0Cy_iE3iO6iuaRo4Ym13pL3-Sxp1i0S5VSKEli78wE='  # اتركه فارغاً لأول مرة

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- وظائف حفظ التقدم ---
def get_last_id():
    if os.path.exists('progress.txt'):
        with open('progress.txt', 'r') as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
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
    
    session_name = 'railway_session'
    
    # إنشاء العميل
    client = TelegramClient(
        session=session_name, 
        api_id=API_ID, 
        api_hash=API_HASH,
        connection_retries=5,
        timeout=60
    )
    
    try:
        # محاولة الاتصال
        logger.info("🔗 محاولة الاتصال بتليجرام...")
        
        if STRING_SESSION:
            # استخدام الجلسة المحفوظة
            logger.info("🔑 استخدام String Session للدخول...")
            client.session = StringSession(STRING_SESSION)
            await client.connect()
            
            if not await client.is_user_authorized():
                logger.warning("❌ الجلسة غير صالحة، جرب الدخول برقم الهاتف")
                await client.start(phone=PHONE_NUMBER)
        else:
            # استخدام رقم الهاتف مباشرة
            logger.info(f"📱 محاولة الدخول بالرقم: {PHONE_NUMBER}")
            await client.start(phone=PHONE_NUMBER)
        
        # التحقق من الدخول
        me = await client.get_me()
        logger.info(f"✅ تم الدخول كـ: {me.first_name} (ID: {me.id})")
        
        # إذا كانت أول مرة، احفظ الـ String Session وعرضه
        if not STRING_SESSION:
            string_session = client.session.save()
            logger.info("=" * 50)
            logger.info("📝 **انسخ هذا الكود وأضفه في الكود مكان STRING_SESSION:**")
            logger.info(f"STRING_SESSION = '{string_session}'")
            logger.info("=" * 50)
        
        logger.info(f"🚀 بدء النقل من الرسالة رقم: {last_saved_id}")
        logger.info(f"📤 من: {SOURCE_CHAT}")
        logger.info(f"📥 إلى: {TO_CHAT}")

        async for message in client.iter_messages(SOURCE_CHAT, reverse=True, offset_id=last_saved_id):
            if isinstance(message, MessageService):
                continue
            
            try:
                # المحاولة الأصلية للإرسال
                await client.send_message(TO_CHAT, message)
                
                # حفظ الرقم فوراً لضمان عدم التكرار
                save_last_id(message.id)
                msg_counter += 1
                
                logger.info(f"✅ تم نقل: {message.id} | العداد: {msg_counter}/1000")

                # نظام الاستراحة المتغيرة (30, 35, 40...60)
                if msg_counter >= 1000:
                    logger.info(f"☕ استراحة مجدولة لمدة {sleep_minutes} دقيقة...")
                    await asyncio.sleep(sleep_minutes * 60)
                    
                    msg_counter = 0
                    sleep_minutes += 5
                    if sleep_minutes > 60:
                        sleep_minutes = 30
                else:
                    # تأخير بسيط جداً (ثانية واحدة) لضمان الاستقرار
                    await asyncio.sleep(1)

            except FloodWaitError as fwe:
                # إذا طلب تيليجرام التوقف
                logger.warning(f"⏳ قيود تيليجرام: انتظار {fwe.seconds} ثانية...")
                await asyncio.sleep(fwe.seconds)
                
            except Exception as e:
                # في حال حدوث أي خطأ
                logger.error(f"❌ خطأ في الرسالة {message.id}: {e}")
                logger.info("محاولة التجاوز والاستمرار في الرسالة التالية...")
                await asyncio.sleep(5)
                continue

    except (AuthKeyError, PhoneNumberInvalidError) as e:
        logger.error(f"❌ خطأ في المصادقة: {e}")
        logger.info("⚠️ تأكد من صحة رقم الهاتف")
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع: {e}")
    finally:
        try:
            await client.disconnect()
            logger.info("🔌 تم قطع الاتصال")
        except:
            pass

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("📱 Telegram Message Forwarder")
    logger.info("🚀 Starting on Railway.app")
    logger.info("=" * 50)
    
    try:
        asyncio.run(forward_job())
    except KeyboardInterrupt:
        logger.info("🛑 تم إوقف البرنامج يدوياً.")
    except Exception as e:
        logger.error(f"💥 خطأ في التشغيل: {e}")
