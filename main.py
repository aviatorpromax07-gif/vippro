import logging
import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
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
from telegram.error import BadRequest, Forbidden

# ================= FIREBASE SETUP (Via Secret File) =================
import firebase_admin
from firebase_admin import credentials, firestore

db = None
FIREBASE_KEY_PATH = "firebase.json"

try:
    if os.path.exists(FIREBASE_KEY_PATH):
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("🔥 Firebase Connected Successfully!")
    else:
        print("⚠️ firebase.json not found! Saving users to users.txt locally.")
except Exception as e:
    print(f"❌ Firebase Init Error: {e}")

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

# --- MEDIA & HACK LINKS ---
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

LOGO_AVIATOR = "https://i.ibb.co/PZBBDv85/images-9.jpg"
LOGO_MINES = "https://i.ibb.co/MDVxth7x/images-8.jpg"
LOGO_PENALTY = "https://i.ibb.co/5WzBdWX4/hqdefault.jpg"
LOGO_KING_THIMBLES = "https://i.ibb.co/8LYwvg1j/maxresdefault.jpg"

LINK_AVIATOR = "https://aviatorbahohacker.fwh.is/"
LINK_MINES = "https://mines-game-hack.netlify.app/"
LINK_PENALTY = "https://pnalteaybot.netlify.app/"
LINK_KING_THIMBLES = "https://kingthimblesbot.netlify.app/"
HOW_TO_USE_LINK = "https://youtube.com/@sunny_bro11?si=gYfOtXnKayCkZloF"

# --- FILES ---
USER_FILE = "users.txt"

# --- CONVERSATION STATES ---
WAITING_FOR_ID = 0
(BROADCAST_SIMPLE, BTN_BROADCAST_CONTENT, BTN_BROADCAST_LABEL, BTN_BROADCAST_LINK, BROADCAST_AUTO_SIGNAL) = range(2, 7)

# --- LANGUAGE CONFIG ---
LANGUAGES = {
    'en': {'name': '🇺🇸 English', 'earn_btn': 'Start Earning Money', 'reg_btn': 'Registration Link', 'verify_btn': '✅ I have Registered (Verify)', 'ask_id': 'Please send your 9-digit Account ID:', 'analyzing': '🔄 Verifying your ID...', 'success_msg': '✅ <b>ACCOUNT VERIFIED!</b>\n\nYour account has been successfully synchronized.', 'play_btn': 'Play With Hack', 'guide_btn': 'How to use', 'help_btn': 'Help', 'select_game': 'Select a game to start hacking:'},
    'hi': {'name': '🇮🇳 India (Hindi)', 'earn_btn': 'पैसे कमाना शुरू करें', 'reg_btn': 'पंजीकरण (Registration)', 'verify_btn': '✅ मैंने पंजीकरण किया है (Verify)', 'ask_id': 'कृपया अपनी 9-अंकीय खाता आईडी भेजें:', 'analyzing': '🔄 खाता जाँचा जा रहा है...', 'success_msg': '✅ <b>खाता सत्यापित!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'उपयोग कैसे करें', 'help_btn': 'मदद (Help)', 'select_game': 'गेम चुनें:'},
    'pk': {'name': '🇵🇰 Pakistan (Urdu)', 'earn_btn': 'پیسہ کمانا شروع کریں', 'reg_btn': 'رجسٹریشن', 'verify_btn': '✅ میں نے رجسٹر کیا ہے (Verify)', 'ask_id': 'براہ کرم اپنی 9 ہندسوں کی اکاؤنٹ آئی ڈی بھیجیں:', 'analyzing': '🔄 چیکنگ...', 'success_msg': '✅ <b>اکاؤنٹ کی تصدیق ہوگئی!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'کیسے استعمال کریں', 'help_btn': 'مدد', 'select_game': 'گیم منتخب کریں:'},
    'bd': {'name': '🇧🇩 Bangladesh (Bangla)', 'earn_btn': 'টাকা আয় শুরু করুন', 'reg_btn': 'রেজিস্ট্রেশন লিংক', 'verify_btn': '✅ আমার রেজিস্ট্রেশন সম্পন্ন হয়েছে', 'ask_id': 'অনুগ্রহ করে আপনার ৯ ডিজিটের একাউন্ট আইডি দিন:', 'analyzing': '🔄 আপনার আইডি যাচাই করা হচ্ছে...', 'success_msg': '✅ <b>একাউন্ট ভেরিফাইড!</b>\n\nআপনার একাউন্টটি সফলভাবে বটের সাথে যুক্ত হয়েছে।', 'play_btn': 'Play With Hack', 'guide_btn': 'কিভাবে ব্যবহার করবেন', 'help_btn': 'সাহায্য', 'select_game': 'হ্যাক শুরু করতে একটি গেম সিলেক্ট করুন:'},
    'id': {'name': '🇮🇩 Indonesia', 'earn_btn': 'Mulai Hasilkan Uang', 'reg_btn': 'Pendaftaran', 'verify_btn': '✅ Saya Sudah Daftar', 'ask_id': 'Kirim ID 9 digit Anda:', 'analyzing': '🔄 Memeriksa...', 'success_msg': '✅ <b>Akun Terverifikasi!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'Cara pakai', 'help_btn': 'Bantuan', 'select_game': 'Pilih Game:'},
    'ru': {'name': '🇷🇺 Russia', 'earn_btn': 'Начать зарабатывать', 'reg_btn': 'Регистрация', 'verify_btn': '✅ Я зарегистрировался', 'ask_id': 'Отправьте ваш ID (9 цифр):', 'analyzing': '🔄 Проверка...', 'success_msg': '✅ <b>Аккаунт подтвержден!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'Как использовать', 'help_btn': 'Помощь', 'select_game': 'Выберите игру:'},
    'tr': {'name': '🇹🇷 Turkey', 'earn_btn': 'Para Kazanmaya Başla', 'reg_btn': 'Kayıt Ol', 'verify_btn': '✅ Kayıt Oldum', 'ask_id': '9 haneli ID nizi gönderin:', 'analyzing': '🔄 Kontrol ediliyor...', 'success_msg': '✅ <b>Hesap Doğrulandı!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'Nasıl kullanılır', 'help_btn': 'Yardım', 'select_game': 'Oyun Seç:'},
    'br': {'name': '🇧🇷 Brazil', 'earn_btn': 'Começar a Ganhar Dinheiro', 'reg_btn': 'Registro', 'verify_btn': '✅ Eu me Registrei', 'ask_id': 'Envie seu ID de 9 dígitos:', 'analyzing': '🔄 Analisando...', 'success_msg': '✅ <b>Conta Verificada!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'Como usar', 'help_btn': 'Ajuda', 'select_game': 'Selecionar Jogo:'}
}

# ================= DATABASE FUNCTIONS =================
def get_users_local():
    if not os.path.exists(USER_FILE):
        return[]
    with open(USER_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def get_users():
    users_set = set(get_users_local())
    if db:
        try:
            docs = db.collection('bot_users').stream()
            for doc in docs:
                users_set.add(doc.id)
        except Exception as e:
            logging.error(f"Firebase fetch error: {e}")
    return list(users_set)

def save_user(user_id):
    user_id_str = str(user_id)
    
    # 1. Local Backup
    users_local = get_users_local()
    if user_id_str not in users_local:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id_str}\n")
            
    # 2. Firebase Save
    if db:
        try:
            doc_ref = db.collection('bot_users').document(user_id_str)
            if not doc_ref.get().exists:
                doc_ref.set({"id": user_id_str})
        except Exception as e:
            logging.error(f"Firebase save error: {e}")

# ================= UTILITY FUNCTIONS =================
async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in[ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except BadRequest:
        return False
    except Exception:
        return False

async def send_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"Hello {user.first_name}, Welcome!\nPlease select your language:"

    keyboard = [[InlineKeyboardButton(LANGUAGES['en']['name'], callback_data='lang_en'),
         InlineKeyboardButton(LANGUAGES['hi']['name'], callback_data='lang_hi')],
        [InlineKeyboardButton(LANGUAGES['pk']['name'], callback_data='lang_pk'),
         InlineKeyboardButton(LANGUAGES['bd']['name'], callback_data='lang_bd')],
        [InlineKeyboardButton(LANGUAGES['id']['name'], callback_data='lang_id'),
         InlineKeyboardButton(LANGUAGES['ru']['name'], callback_data='lang_ru')],[InlineKeyboardButton(LANGUAGES['tr']['name'], callback_data='lang_tr'),
         InlineKeyboardButton(LANGUAGES['br']['name'], callback_data='lang_br')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.delete()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text, reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text, reply_markup=reply_markup)

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id) 
    
    is_member = await check_membership(user_id, context)
    
    if is_member:
        await send_language_menu(update, context)
    else:
        join_text = "⚠️ <b>Action Required!</b>\n\nTo use this bot, you must join our official Private channel first.\nPlease join the channel and click 'Joined' button below."
        keyboard = [[InlineKeyboardButton("📢 Join Private Channel", url=CHANNEL_LINK)],[InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join_status')]]
        await context.bot.send_message(chat_id=user_id, text=join_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    return ConversationHandler.END

async def restart_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)
    return ConversationHandler.END

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    if await check_membership(user_id, context):
        await query.answer("✅ Verification Successful!")
        await send_language_menu(update, context)
    else:
        await query.answer("❌ You have not joined yet! Please join the channel first.", show_alert=True)

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data.split('_')[1]
    context.user_data['selected_lang'] = lang_code
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    keyboard = [[InlineKeyboardButton(lang_data['earn_btn'], callback_data='start_earning')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    try:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_WELCOME, caption=f"Language: {lang_data['name']}\n\nClick below to proceed:", reply_markup=reply_markup)
    except Exception:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Click below to start:", reply_markup=reply_markup)
    return ConversationHandler.END

async def show_registration_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    info_text = "<b>Step 1- Register.</b>\n\nTo synchronize with the bot, you need to create a new account strictly via the link from the bot and use the promo code <b>BLACK110</b>\n\nIf you opened the link and accessed an old account, you need to:\n- Log out of the old account\n- Close the website\n- Reopen the link from the bot's button\n\n<b>2- Complete the registration</b>\n\nAfter successful registration, click the <b>Verify</b> button below."
    keyboard = [[InlineKeyboardButton(f"🔗 {lang_data['reg_btn']}", url="https://1wezue.com/casino")],[InlineKeyboardButton(f"{lang_data['verify_btn']}", callback_data='verify_reg')],[InlineKeyboardButton(f"🆘 {lang_data['help_btn']}", url="https://t.me/SUNNY_BRO1")]]
    await query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_REG, caption=info_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def verify_process_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    lang_data = LANGUAGES.get(context.user_data.get('selected_lang', 'en'), LANGUAGES['en'])

    msg = await context.bot.send_message(chat_id=chat_id, text="⏳ Checking synchronization... Please wait 5 seconds.")
    await asyncio.sleep(5) 
    try: await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    except: pass
    await context.bot.send_message(chat_id=chat_id, text=lang_data['ask_id'])
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_text = update.message.text.strip()
    user = update.effective_user
    chat_id = update.effective_chat.id
    lang_data = LANGUAGES.get(context.user_data.get('selected_lang', 'en'), LANGUAGES['en'])

    analyzing_msg = await update.message.reply_text(f"⏳ {lang_data['analyzing']}")
    admin_text = f"🚨 <b>New Auto-Verified User!</b>\n👤 Name: {user.first_name}\n🆔 Telegram ID: {user.id}\n📝 <b>1Win ID:</b> <code>{user_id_text}</code>\n✅ <i>Bot has auto-approved this user.</i>"
    try: await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode='HTML')
    except Exception: pass

    await asyncio.sleep(2)
    try: await context.bot.delete_message(chat_id=chat_id, message_id=analyzing_msg.message_id)
    except: pass

    keyboard = [[InlineKeyboardButton(f"🎮 {lang_data['play_btn']}", callback_data='play_hack_action')],[InlineKeyboardButton(f"📺 {lang_data['guide_btn']}", url=HOW_TO_USE_LINK)]]
    await context.bot.send_photo(chat_id=chat_id, photo=IMAGE_URL_SUCCESS, caption=lang_data['success_msg'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def play_hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_data = LANGUAGES.get(context.user_data.get('selected_lang', 'en'), LANGUAGES['en'])

    keyboard = [[InlineKeyboardButton("✈️ Aviator", callback_data='game_aviator')],[InlineKeyboardButton("💣 Mines", callback_data='game_mines')],[InlineKeyboardButton("⚽ Penalty", callback_data='game_penalty')],[InlineKeyboardButton("👑 King Thimbles", callback_data='game_king_thimbles')]]
    try: await query.message.delete()
    except: pass
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_HACK_MENU, caption=lang_data['select_game'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def game_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logos = {'game_aviator': (LOGO_AVIATOR, "Aviator", LINK_AVIATOR), 'game_mines': (LOGO_MINES, "Mines", LINK_MINES), 'game_penalty': (LOGO_PENALTY, "Penalty", LINK_PENALTY), 'game_king_thimbles': (LOGO_KING_THIMBLES, "King Thimbles", LINK_KING_THIMBLES)}
    logo_url, game_name, hack_url = logos.get(query.data, logos['game_aviator'])

    keyboard = [[InlineKeyboardButton(f"📱 Open {game_name} Hack", web_app=WebAppInfo(url=hack_url))],[InlineKeyboardButton("🔙 Back", callback_data='play_hack_action')]]
    try: await query.message.delete()
    except: pass
    try:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=logo_url, caption=f"<b>{game_name} Hack Connected!</b>\n\nClick the button below to access the hack tool.", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"<b>{game_name} Selected.</b>\nClick below:", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# ================= ADMIN HANDLERS =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return ConversationHandler.END
    users = get_users()
    msg = f"👑 <b>ADMIN PANEL</b> 👑\n\n👥 <b>Total Users:</b> {len(users)}\nChoose an option below:"
    keyboard = [[InlineKeyboardButton("📝 Plain Broadcast", callback_data='admin_simple_broadcast')],[InlineKeyboardButton("🔗 Custom Button Broadcast", callback_data='admin_btn_broadcast')],[InlineKeyboardButton("✨ Signal Broadcast (Auto Button)", callback_data='admin_auto_signal_broadcast')],[InlineKeyboardButton("❌ Close", callback_data='admin_close')]]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    return ConversationHandler.END

async def start_simple_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.edit_text("📝 <b>Plain Broadcast Mode</b>\n\nSend message (Text or Photo).\nType /cancel to cancel.", parse_mode='HTML')
    return BROADCAST_SIMPLE

async def perform_simple_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_users()
    count = 0
    status_msg = await update.message.reply_text(f"🚀 Sending Plain Broadcast to {len(users)} users...")
    for uid in users:
        try:
            if update.message.photo: await context.bot.send_photo(chat_id=int(uid), photo=update.message.photo[-1].file_id, caption=update.message.caption if update.message.caption else "")
            else: await context.bot.send_message(chat_id=int(uid), text=update.message.text)
            count += 1
        except Exception: pass
        await asyncio.sleep(0.05)
    await status_msg.edit_text(f"✅ Plain Broadcast Sent to {count} users.")
    return ConversationHandler.END

async def start_btn_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.edit_text("🔗 <b>Custom Button Broadcast</b>\n\nStep 1: Send Message Content.\nType /cancel to cancel.", parse_mode='HTML')
    return BTN_BROADCAST_CONTENT

async def get_btn_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['bc_type'] = 'photo'
        context.user_data['bc_photo'] = update.message.photo[-1].file_id
        context.user_data['bc_caption'] = update.message.caption if update.message.caption else ""
    else:
        context.user_data['bc_type'] = 'text'
        context.user_data['bc_text'] = update.message.text
    await update.message.reply_text("Step 2: Enter <b>Button Name</b>", parse_mode='HTML')
    return BTN_BROADCAST_LABEL

async def get_btn_label(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bc_btn_label'] = update.message.text
    await update.message.reply_text("Step 3: Enter <b>Button URL</b>\n\n(Must start with http:// or https://)", parse_mode='HTML')
    return BTN_BROADCAST_LINK

async def perform_btn_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    if not link.startswith(('http://', 'https://')): link = 'https://' + link
    label = context.user_data['bc_btn_label']
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(label, url=link)]])
    users = get_users()
    count = 0
    status_msg = await update.message.reply_text(f"🚀 Sending Custom Button Broadcast to {len(users)} users...")
    for uid in users:
        try:
            if context.user_data['bc_type'] == 'photo': await context.bot.send_photo(chat_id=int(uid), photo=context.user_data['bc_photo'], caption=context.user_data['bc_caption'], reply_markup=reply_markup)
            else: await context.bot.send_message(chat_id=int(uid), text=context.user_data['bc_text'], reply_markup=reply_markup)
            count += 1
        except Exception: pass
        await asyncio.sleep(0.05)
    await status_msg.edit_text(f"✅ Custom Button Broadcast Sent to {count} users.")
    return ConversationHandler.END

async def start_auto_signal_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.edit_text("✨ <b>Signal Broadcast Mode</b>\n\nSend message (Text or Photo).\n'GET SIGNAL✨' button will be added automatically.\nType /cancel to cancel.", parse_mode='HTML')
    return BROADCAST_AUTO_SIGNAL

async def perform_auto_signal_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_users()
    count = 0
    status_msg = await update.message.reply_text(f"🚀 Sending Signal Broadcast to {len(users)} users...")
    auto_markup = InlineKeyboardMarkup([[InlineKeyboardButton("GET SIGNAL✨", callback_data='restart_bot_action')]])
    for uid in users:
        try:
            if update.message.photo: await context.bot.send_photo(chat_id=int(uid), photo=update.message.photo[-1].file_id, caption=update.message.caption if update.message.caption else "", reply_markup=auto_markup)
            else: await context.bot.send_message(chat_id=int(uid), text=update.message.text, reply_markup=auto_markup)
            count += 1
        except Exception: pass
        await asyncio.sleep(0.05)
    await status_msg.edit_text(f"✅ Signal Broadcast Sent to {count} users.")
    return ConversationHandler.END

async def close_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Admin Panel Closed")
    try: await update.callback_query.message.delete()
    except Exception: pass
    return ConversationHandler.END 

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message: await update.message.reply_text("❌ Action Cancelled. Send /start to restart.")
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    if not os.path.exists(USER_FILE): open(USER_FILE, 'w').close()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    verify_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_process_start, pattern='^verify_reg$')],
        states={WAITING_FOR_ID:[MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('admin', admin_panel)],
        allow_reentry=True
    )

    admin_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_simple_broadcast, pattern='^admin_simple_broadcast$'),
            CallbackQueryHandler(start_btn_broadcast, pattern='^admin_btn_broadcast$'),
            CallbackQueryHandler(start_auto_signal_broadcast, pattern='^admin_auto_signal_broadcast$')
        ],
        states={
            BROADCAST_SIMPLE:[MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, perform_simple_broadcast)],
            BTN_BROADCAST_CONTENT:[MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, get_btn_content)],
            BTN_BROADCAST_LABEL:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_btn_label)],
            BTN_BROADCAST_LINK:[MessageHandler(filters.TEXT & ~filters.COMMAND, perform_btn_broadcast)],
            BROADCAST_AUTO_SIGNAL:[MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, perform_auto_signal_broadcast)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel), 
            CommandHandler('admin', admin_panel),
            CallbackQueryHandler(close_admin, pattern='^admin_close$')
        ],
        allow_reentry=True
    )

    application.add_handler(verify_conv)
    application.add_handler(admin_conv)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('admin', admin_panel))
    
    application.add_handler(CallbackQueryHandler(check_join_callback, pattern='^check_join_status$'))
    application.add_handler(CallbackQueryHandler(language_handler, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(show_registration_info, pattern='^start_earning$'))
    application.add_handler(CallbackQueryHandler(play_hack_menu, pattern='^play_hack_action$'))
    application.add_handler(CallbackQueryHandler(game_selection_handler, pattern='^game_'))
    application.add_handler(CallbackQueryHandler(close_admin, pattern='^admin_close$'))
    application.add_handler(CallbackQueryHandler(restart_bot_handler, pattern='^restart_bot_action$'))

    print("Bot is perfectly running...✅")
    application.run_polling()
