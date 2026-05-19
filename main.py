import logging
import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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
from telegram.error import BadRequest

# ================= FIREBASE SETUP =================
# আপনার ডাউনলোড করা JSON ফাইলটির নাম এখানে দিন
CREDENTIALS_FILE = "firebase_credentials.json"
# আপনার ফায়ারবেস ডেটাবেসের URL (Render Environment Variable থেকে নেবে অথবা এখানে সরাসরি দিতে পারেন)
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL", "https://telegrambotdb-d2b45-default-rtdb.asia-southeast1.firebasedatabase.app/")

# ফায়ারবেস ইনিশিয়ালাইজ করা
try:
    cred = credentials.Certificate(CREDENTIALS_FILE)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_DB_URL
    })
    print("Firebase connected successfully! ✅")
except Exception as e:
    print(f"Error connecting to Firebase: {e}")

# ================= RENDER DUMMY SERVER =================
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is perfectly running on Render with Firebase!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

# ================= CONFIGURATION =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8525057709:AAE6kuNKFx1xtsp7HvhJygTXZZval9iE278")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1146186608"))
REQUIRED_CHANNEL = int(os.getenv("REQUIRED_CHANNEL", "-1001481593780"))
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# --- MEDIA & LINKS ---
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

LOGO_AVIATOR = "https://i.ibb.co/PZBBDv85/images-9.jpg"
LOGO_MINES = "https://i.ibb.co/MDVxth7x/images-8.jpg"
LOGO_PENALTY = "https://i.ibb.co/5WzBdWX4/hqdefault.jpg"
LOGO_KING_THIMBLES = "https://i.ibb.co/8LYwvg1j/maxresdefault.jpg"

LINK_AVIATOR = "https://aviatorgameadmin.netlify.app/"
LINK_MINES = "https://mines-game-hack.netlify.app/"
LINK_PENALTY = "https://pnalteaybot.netlify.app/"
LINK_KING_THIMBLES = "https://kingthimblesbot.netlify.app/"
HOW_TO_USE_LINK = "https://youtube.com/@sunny_bro11?si=gYfOtXnKayCkZloF"

# --- CONVERSATION STATES ---
WAITING_FOR_ID = 0
(BROADCAST_SIMPLE, BTN_BROADCAST_CONTENT, BTN_BROADCAST_LABEL, BTN_BROADCAST_LINK, BROADCAST_AUTO_SIGNAL) = range(2, 7)

# --- LANGUAGE CONFIG ---
LANGUAGES = {
    'en': {'name': '🇺🇸 English', 'earn_btn': 'Start Earning Money', 'reg_btn': 'Registration Link', 'verify_btn': '✅ I have Registered (Verify)', 'ask_id': 'Please send your 9-digit Account ID:', 'analyzing': '🔄 Verifying your ID...', 'success_msg': '✅ <b>ACCOUNT VERIFIED!</b>\n\nYour account has been successfully synchronized.', 'play_btn': 'Play With Hack', 'guide_btn': 'How to use', 'help_btn': 'Help', 'select_game': 'Select a game to start hacking:'},
    # (আপনার অন্যান্য ভাষাগুলো আগের মতই থাকবে, আমি সংক্ষেপের জন্য শুধু EN রাখিনি, সবগুলোই ঠিকভাবে কাজ করবে। আপনি চাইলে আপনার আগের ভাষার ডিকশনারিটি এখানে হুবহু রিপ্লেস করে দিতে পারেন।)
}

# ================= FIREBASE DATABASE FUNCTIONS =================
def save_user(user_id):
    """ইউজার ফায়ারবেসে না থাকলে নতুন করে সেভ করবে"""
    try:
        ref = db.reference('users')
        user_ref = ref.child(str(user_id))
        
        # যদি ইউজারের ডেটা আগে থেকে না থাকে
        if not user_ref.get():
            user_ref.set({
                "status": "active"
            })
    except Exception as e:
        logging.error(f"Error saving to Firebase: {e}")

def get_users():
    """ফায়ারবেস থেকে সব ইউজারের লিস্ট নিয়ে আসবে ব্রডকাস্টের জন্য"""
    try:
        ref = db.reference('users')
        users_data = ref.get()
        if users_data:
            return list(users_data.keys())
        return []
    except Exception as e:
        logging.error(f"Error fetching from Firebase: {e}")
        return []

# ================= UTILITY FUNCTIONS =================
async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except BadRequest:
        return False
    except Exception:
        return False

async def send_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"Hello {user.first_name}, Welcome!\nPlease select your language:"
    keyboard = [[InlineKeyboardButton('🇺🇸 English', callback_data='lang_en')]] # (এখানে আপনার আগের কীবোর্ড বসিয়ে নেবেন)
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.delete()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text, reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text, reply_markup=reply_markup)

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Firebase-এ ইউজার সেভ করা হচ্ছে
    save_user(user_id)
    
    is_member = await check_membership(user_id, context)
    
    if is_member:
        await send_language_menu(update, context)
    else:
        join_text = (
            "⚠️ <b>Action Required!</b>\n\n"
            "To use this bot, you must join our official Private channel first.\n"
            "Please join the channel and click 'Joined' button below."
        )
        keyboard = [
            [InlineKeyboardButton("📢 Join Private Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join_status')]
        ]
        await context.bot.send_message(
            chat_id=user_id, text=join_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML'
        )
    return ConversationHandler.END

# (আপনার বাকি হ্যান্ডলারগুলো যেমন check_join_callback, show_registration_info, verify_process_start, receive_id ইত্যাদি হুবহু আগের মতোই থাকবে, সেগুলোতে কোনো পরিবর্তন করার দরকার নেই)

# ================= ADMIN HANDLERS =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    users = get_users() # এখন এটি ফায়ারবেস থেকে লাইভ ডাটা আনবে!
    msg = (
        f"👑 <b>ADMIN PANEL</b> 👑\n\n"
        f"👥 <b>Total Users (Firebase):</b> {len(users)}\n"
        f"Choose an option below:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📝 Plain Broadcast", callback_data='admin_simple_broadcast')],
        [InlineKeyboardButton("🔗 Custom Button Broadcast", callback_data='admin_btn_broadcast')],
        [InlineKeyboardButton("✨ Signal Broadcast", callback_data='admin_auto_signal_broadcast')],
        [InlineKeyboardButton("❌ Close", callback_data='admin_close')]
    ]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    return ConversationHandler.END

# (ব্রডকাস্টের বাকি হ্যান্ডলারগুলো আগের মতোই থাকবে, কারণ get_users() ফাংশনটি এখন সরাসরি ফায়ারবেস থেকে ডাটা সাপ্লাই দেবে)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("❌ Action Cancelled. Send /start to restart.")
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    threading.Thread(target=run_dummy_server, daemon=True).start()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # (আগের মতোই Handler যুক্ত করুন)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('admin', admin_panel))
    # ... বাকি সব হ্যান্ডলার ...

    print("Bot is perfectly running with Firebase...✅")
    application.run_polling()
