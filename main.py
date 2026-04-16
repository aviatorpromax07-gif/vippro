import logging
import asyncio
import os
import json
from threading import Thread
from flask import Flask
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember, WebAppInfo
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ConversationHandler
)

# ================= LOGGING =================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= FIREBASE SETUP =================
firebase_config = {
  "type": "service_account",
  "project_id": "winbot-eea9a",
  "private_key_id": "0fc394504ed2eb8954ec426bbe11f46eec38ffb0",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDGPOJtItY6HTIS\nqr+K+wiVmjaa1hl+qpRlHH6AjdUHVEIoVteooVHleZW/XlJZRyNMnp0fnqcChb/9\n5uXbLreay1UEnmwFUmxoqGADbxh9FSrCoyczrIGXr3EfoENxH9wVU8dtwlK6g1fY\nl0e8btmweoTsDt8qCA1BfaOBKccWCFkkg2wu8zVqghTOCw09/upzgTPALvuwDcDC\nWNpYzj87y2j+f2CMdu4RRiDZ+VosIIhSAAV1Y193UELcZDTv5/Wlj6mbKWb+O0xK\n8Yp5Z3LS/Yg4T+IsDHCxmk+3Ul3qPNb8Avuy0HuWBEgwj4rqxBoMMTjUIopp1h69\nxzbFkKu7AgMBAAECggEAAXVeNxkBWXvF1rRR5McJs6Fm/cb4eLbu5jrfmrjbFIrj\n/QxShDJCT31lrXrsq9fQTyvVkm97jBMJgWfgULdXG3jxKa+0B2qpUzB18GCHXhg4\nmyZRz1lZZLvM3xjclimlWAoolp/44C1qM9+SZApZaKkmGYnXI3sxWcYqXJ9pkGRr\nrSPZw77hY3H+2ByNO6mBGYR+yecjvTOUcBZuIqgkEmv+dRhec/QllmXZCDTYyWWM\nj6iAA1ARAQ9tep5tsv4tDUI801v24SJ0ulQLDFvaEZ16fSBu0fTnjDYeK8ukSQYB\nNfUbfGQRLeeii8XCktPtP47Vda5x9kM3ANRJdJ7FmQKBgQDwLRqqKXgjumOmY78F\ndvP/p5iYaH1nsEJ6m/JxgzyHIwhu1xS7v7KRyjLZyxTD614FK15qh3nX0A/Q2+M5\nQywNhMXnPPB01tMsFJTFKVb7TBa9XcVtQcV7XPHugceKAFUp3nQC1sw1lKKluFWb\nvuXKdkigHJ4EiNWERgoBfjyv6QKBgQDTTG7qDldWLs8UXVglwBpaMXGw/PEJxkiW\n8MHKCbhEfwU7PCB2yoB3mN+5tjPJ49g28J7FaklIwjBRxGFP3rVVtnJ2vyQzfr6n\nL1D6jAZUPLjmUWx8rCB2jWFL7eBxVlPc63tE33CMGpxq8oiBkyKsPf61pRLqNEP6\nzzCJIKA8AwKBgQCPi1WRd+F+8QpXyuvDF1ozZPZ1uJWi4ByLbSMUpswJNG342QFi\SOsv6TpFIvQROF3kFwyB/OBclNSvDoyaj8QHfGBPmQNZwX9KrC5SPCfpX4uDuESj\nzRh7Z4yM8PHST+qWcIbDn59DMseW5jn8MLbkL5euYgwrR6DdQoL+a3VX6QKBgQCC\nKe+Zl8QNf0Bp1ybZ+oFBVnwm/2qtDszgzudSQrKU33qlhuCozQ5ennoTuT4l/InR\nLmFgU51ZiOajOEqKHTOv3Xid1hnC7y0baHaGIYQ0mEN+/mHKW26UGXv6fktpBjkb\nOqTxRIPcivgYmdelmrIdUQN7enkwdYn7E29eyg5raQKBgG/kppUI/hJy0sA2TkWW\nIS/poxxHLw3VO2mNDJKhW+n1okzJ2x3Ftx3han2AlAUXmLXiOH+R0GKRpT7Xtz8J\nDP4rNxnZJ8smPuWIC4YbI9kEDrF4Pgd2USmawrycMqZdcTJ6jtSMHUdVJoTbgyd1\nicEVdXxDzM5IGdi42DcSyGBB\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@winbot-eea9a.iam.gserviceaccount.com",
}

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://winbot-eea9a-default-rtdb.firebaseio.com/"
        })
    logger.info("✅ Firebase connected!")
except Exception as e:
    logger.error(f"❌ Firebase Error: {e}")

# ================= CONFIGURATION =================
BOT_TOKEN = "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q"
ADMIN_ID = 1146186608
REQUIRED_CHANNEL = -1001481593780
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# Media
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

# ================= DATABASE FUNC =================
def save_user(user):
    ref = db.reference(f'users/{user.id}')
    if not ref.get():
        ref.set({
            'first_name': user.first_name,
            'username': user.username or "N/A",
            'id': user.id
        })

def get_all_users():
    ref = db.reference('users')
    users = ref.get()
    return list(users.keys()) if users else []

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    
    # মেম্বারশিপ চেক
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user.id)
        is_member = member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except: is_member = False
    
    if is_member:
        keyboard = [[InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'),
                     InlineKeyboardButton("🇧🇩 বাংলা", callback_data='lang_bd')]]
        await update.message.reply_photo(photo=IMAGE_URL_WELCOME, caption="Select Language / ভাষা নির্বাচন করুন:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join')]]
        await update.message.reply_text("⚠️ Join our channel first!", reply_markup=InlineKeyboardMarkup(keyboard))

async def language_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['selected_lang'] = lang
    
    text = "🚀 <b>Register Now!</b>\nUse promo <code>BLACK696</code> to activate hack." if lang == 'en' else "🚀 <b>রেজিস্ট্রেশন করুন!</b>\nহ্যাক অ্যাক্টিভেট করতে প্রোমো <code>BLACK696</code> ব্যবহার করুন।"
    btn_text = "🔗 Registration Link" if lang == 'en' else "🔗 রেজিস্ট্রেশন লিংক"
    verify_btn = "✅ I have Registered" if lang == 'en' else "✅ রেজিস্ট্রেশন সম্পন্ন হয়েছে"
    
    keyboard = [[InlineKeyboardButton(btn_text, url="https://bit.ly/3S0V67h")],
                [InlineKeyboardButton(verify_btn, callback_data='verify_reg')]]
    
    await query.message.delete()
    await context.bot.send_photo(chat_id=query.message.chat_id, photo=IMAGE_URL_REG, caption=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

# আইডি ভেরিফাই প্রসেস (৫ সেকেন্ড ওয়েট)
WAITING_FOR_ID = 0
async def verify_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('selected_lang', 'en')
    
    wait_text = "⏳ Verifying synchronization... Please wait 5s." if lang == 'en' else "⏳ সিঙ্ক্রোনাইজেশন যাচাই করা হচ্ছে... ৫ সেকেন্ড অপেক্ষা করুন।"
    msg = await query.message.reply_text(wait_text)
    await asyncio.sleep(5)
    await msg.delete()
    
    ask_text = "Please send your 9-digit Account ID:" if lang == 'en' else "আপনার ৯ ডিজিটের আইডি পাঠান:"
    await query.message.reply_text(ask_text)
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_val = update.message.text
    lang = context.user_data.get('selected_lang', 'en')
    
    # অ্যাডমিন নোটিফিকেশন
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"🚨 <b>New ID Submitted:</b> <code>{user_id_val}</code>", parse_mode='HTML')
    
    success_text = "✅ <b>Verified!</b> Account linked." if lang == 'en' else "✅ <b>ভেরিফাইড!</b> একাউন্ট যুক্ত হয়েছে।"
    keyboard = [[InlineKeyboardButton("🎮 Open Hack", callback_data='open_hack')]]
    
    await update.message.reply_photo(photo=IMAGE_URL_SUCCESS, caption=success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    return ConversationHandler.END

async def hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("✈️ Aviator", web_app=WebAppInfo(url="https://aviatorbahohacker.fwh.is/"))],
        [InlineKeyboardButton("💣 Mines", web_app=WebAppInfo(url="https://mines-game-hack.netlify.app/"))]
    ]
    await context.bot.send_photo(chat_id=query.message.chat_id, photo=IMAGE_HACK_MENU, caption="Select Game:", reply_markup=InlineKeyboardMarkup(keyboard))

# ================= ADMIN PANEL =================
BC_CONTENT, BC_LABEL, BC_LINK = range(1, 4)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users = get_all_users()
    keyboard = [[InlineKeyboardButton("🔗 Button Broadcast", callback_data='admin_bc')]]
    await update.message.reply_text(f"🛠 <b>Admin Panel</b>\nTotal Users: {len(users)}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def bc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Send Message (Text/Photo):")
    return BC_CONTENT

async def bc_get_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['bc_type'] = 'photo'
        context.user_data['bc_file'] = update.message.photo[-1].file_id
        context.user_data['bc_cap'] = update.message.caption
    else:
        context.user_data['bc_type'] = 'text'
        context.user_data['bc_text'] = update.message.text
    await update.message.reply_text("Enter Button Text:")
    return BC_LABEL

async def bc_get_label(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bc_label'] = update.message.text
    await update.message.reply_text("Enter Button URL:")
    return BC_LINK

async def bc_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    label = context.user_data['bc_label']
    users = get_all_users()
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(label, url=url)]])
    
    count = 0
    for uid in users:
        try:
            if context.user_data['bc_type'] == 'photo':
                await context.bot.send_photo(uid, photo=context.user_data['bc_file'], caption=context.user_data['bc_cap'], reply_markup=markup)
            else:
                await context.bot.send_message(uid, text=context.user_data['bc_text'], reply_markup=markup)
            count += 1
            await asyncio.sleep(0.05)
        except: pass
    await update.message.reply_text(f"✅ Sent to {count} users.")
    return ConversationHandler.END

# ================= AUTO MESSAGE (3 HOURS) =================
async def auto_broadcast_job(context: ContextTypes.DEFAULT_TYPE):
    users = get_all_users()
    text = "🚀 <b>New Hack Update!</b>\nআমাদের নতুন সিগন্যাল চেক করুন এবং প্রফিট করুন।\n\n[3-Hour Reminder]"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎮 ওপেন হ্যাক", url="https://t.me/SUNNY_BRO1")]])
    
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=text, reply_markup=keyboard, parse_mode='HTML')
            await asyncio.sleep(0.05)
        except: pass

# ================= WEB SERVER =================
app_server = Flask(__name__)
@app_server.route('/')
def home(): return "Bot is Online"
def run_web(): app_server.run(host='0.0.0.0', port=8080)

# ================= MAIN =================
if __name__ == '__main__':
    Thread(target=run_web).start()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Job Queue for 3-Hour Auto Message (10800 seconds)
    bot_app.job_queue.run_repeating(auto_broadcast_job, interval=10800, first=10)

    # Handlers
    user_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_start, pattern='^verify_reg$')],
        states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
        fallbacks=[CommandHandler('start', start)]
    )
    
    admin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(bc_start, pattern='^admin_bc$')],
        states={
            BC_CONTENT: [MessageHandler(filters.ALL & ~filters.COMMAND, bc_get_content)],
            BC_LABEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bc_get_label)],
            BC_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, bc_done)],
        },
        fallbacks=[CommandHandler('admin', admin_panel)]
    )

    bot_app.add_handler(CommandHandler('start', start))
    bot_app.add_handler(CommandHandler('admin', admin_panel))
    bot_app.add_handler(user_conv)
    bot_app.add_handler(admin_conv)
    bot_app.add_handler(CallbackQueryHandler(language_select, pattern='^lang_'))
    bot_app.add_handler(CallbackQueryHandler(hack_menu, pattern='^open_hack$'))
    bot_app.add_handler(CallbackQueryHandler(start, pattern='^check_join$'))

    print("Bot is running with Firebase and Auto-Broadcast...")
    bot_app.run_polling()
