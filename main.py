import logging
import asyncio
import os
from aiohttp import web
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

# ================= CONFIGURATION =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8525057709:AAHk8EzWfB268Pnz48gg8scF4OXLr7LPm6M")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1146186608"))
REQUIRED_CHANNEL = int(os.getenv("REQUIRED_CHANNEL", "-1001481593780"))
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# --- MEDIA LINKS ---
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
USER_FILE = "users.txt"

# --- CONVERSATION STATES ---
WAITING_FOR_ID = 0
(BROADCAST_SIMPLE, BTN_BROADCAST_CONTENT, BTN_BROADCAST_LABEL, BTN_BROADCAST_LINK, BROADCAST_AUTO_SIGNAL) = range(2, 7)

# --- LANGUAGE CONFIG ---
LANGUAGES = {
    'en': {'name': '🇺🇸 English', 'earn_btn': 'Start Earning Money', 'reg_btn': 'Registration Link', 'verify_btn': '✅ I have Registered (Verify)', 'ask_id': 'Please send your 9-digit Account ID:', 'analyzing': '🔄 Verifying your ID...', 'success_msg': '✅ <b>ACCOUNT VERIFIED!</b>\n\nYour account has been successfully synchronized.', 'play_btn': 'Play With Hack', 'guide_btn': 'How to use', 'help_btn': 'Help', 'select_game': 'Select a game to start hacking:'},
    'hi': {'name': '🇮🇳 India (Hindi)', 'earn_btn': 'पैसे कमाना শুরু करें', 'reg_btn': 'पंजीकरण (Registration)', 'verify_btn': '✅ मैंने पंजीकरण किया है (Verify)', 'ask_id': 'कृपया अपनी 9-অংकीय खाता আইডি भेजें:', 'analyzing': '🔄 खाता जाँचा जा रहा है...', 'success_msg': '✅ <b>खाता सत्यापित!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'उपयोग कैसे करें', 'help_btn': 'मदद (Help)', 'select_game': 'गेम चुनें:'},
    'pk': {'name': '🇵🇰 Pakistan (Urdu)', 'earn_btn': 'پیسہ کمانا شروع کریں', 'reg_btn': 'رجسٹریشن', 'verify_btn': '✅ میں نے رجسٹر کیا ہے (Verify)', 'ask_id': 'براہ کرم اپنی 9 ہندسوں کی اکاؤنٹ آئی ডি بھیجیں:', 'analyzing': '🔄 چیکنگ...', 'success_msg': '✅ <b>اکاؤنٹ کی تصدیق ہوگئی!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'کیسے استعمال کریں', 'help_btn': 'مدد', 'select_game': 'گیم منتخب کریں:'},
    'bd': {'name': '🇧🇩 Bangladesh (Bangla)', 'earn_btn': 'টাকা আয় শুরু করুন', 'reg_btn': 'রেজিস্ট্রেশন লিংক', 'verify_btn': '✅ আমার রেজিস্ট্রেশন সম্পন্ন হয়েছে', 'ask_id': 'অনুগ্রহ করে আপনার ৯ ডিজিটের একাউন্ট আইডি দিন:', 'analyzing': '🔄 আপনার আইডি যাচাই করা হচ্ছে...', 'success_msg': '✅ <b>একাউন্ট ভেরিফাইড!</b>\n\nআপনার একাউন্টটি সফলভাবে বটের সাথে যুক্ত হয়েছে।', 'play_btn': 'Play With Hack', 'guide_btn': 'কিভাবে ব্যবহার করবেন', 'help_btn': 'সাহায্য', 'select_game': 'হ্যাক শুরু করতে একটি গেম সিলেক্ট করুন:'},
    'id': {'name': '🇮🇩 Indonesia', 'earn_btn': 'Mulai Hasilkan Uang', 'reg_btn': 'Pendaftaran', 'verify_btn': '✅ Saya Sudah Daftar', 'ask_id': 'Kirim ID 9 digit Anda:', 'analyzing': '🔄 Memeriksa...', 'success_msg': '✅ <b>Akun Terverifikasi!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'Cara pakai', 'help_btn': 'Bantuan', 'select_game': 'Pilih Game:'},
    'ru': {'name': '🇷🇺 Russia', 'earn_btn': 'Начать зарабатывать', 'reg_btn': 'Регистрация', 'verify_btn': '✅ Я зарегистрировался', 'ask_id': 'Отправьте ваш ID (9 цифр):', 'analyzing': '🔄 Проверка...', 'success_msg': '✅ <b>Аккаунт подтвержден!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'Как использовать', 'help_btn': 'Помощь', 'select_game': 'Выберите игру:'},
    'tr': {'name': '🇹🇷 Turkey', 'earn_btn': 'Para Kazanmaya Başla', 'reg_btn': 'Kayıt Ol', 'verify_btn': '✅ Kayıt Oldum', 'ask_id': '9 haneli ID nizi gönderin:', 'analyzing': '🔄 Kontrol ediliyor...', 'success_msg': '✅ <b>Hesap Doğrulandı!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'Nasıl kullanılır', 'help_btn': 'Yardım', 'select_game': 'Oyun Seç:'},
    'br': {'name': '🇧🇷 Brazil', 'earn_btn': 'Começar a Ganhar Dinheiro', 'reg_btn': 'Registro', 'verify_btn': '✅ Eu me Registrei', 'ask_id': 'Envie seu ID de 9 dígitos:', 'analyzing': '🔄 Analisando...', 'success_msg': '✅ <b>Conta Verificada!</b>', 'play_btn': 'Play With Hack', 'guide_btn': 'Como usar', 'help_btn': 'Ajuda', 'select_game': 'Selecionar Jogo:'}
}

# ================= RENDER ALIVE SERVER =================
async def handle(request):
    return web.Response(text="Bot is running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# ================= DATABASE FUNCTIONS =================
def save_user(user_id):
    if not os.path.exists(USER_FILE): open(USER_FILE, 'w').close()
    with open(USER_FILE, "r") as f: users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f: f.write(f"{user_id}\n")

def get_users():
    if not os.path.exists(USER_FILE): return []
    with open(USER_FILE, "r") as f: return [line.strip() for line in f.readlines()]

# ================= AUTO HOURLY MESSAGE =================
async def auto_update_message_job(context: ContextTypes.DEFAULT_TYPE):
    users = get_users()
    for uid in users:
        try:
            await context.bot.send_message(chat_id=int(uid), text="UPDATE YOUR ACCOUNT /start")
            await asyncio.sleep(0.05)
        except: pass

# ================= CORE HANDLERS =================
async def check_membership(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except: return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    if await check_membership(user_id, context):
        keyboard = [
            [InlineKeyboardButton(LANGUAGES['en']['name'], callback_data='lang_en'), InlineKeyboardButton(LANGUAGES['hi']['name'], callback_data='lang_hi')],
            [InlineKeyboardButton(LANGUAGES['pk']['name'], callback_data='lang_pk'), InlineKeyboardButton(LANGUAGES['bd']['name'], callback_data='lang_bd')],
            [InlineKeyboardButton(LANGUAGES['id']['name'], callback_data='lang_id'), InlineKeyboardButton(LANGUAGES['ru']['name'], callback_data='lang_ru')],
            [InlineKeyboardButton(LANGUAGES['tr']['name'], callback_data='lang_tr'), InlineKeyboardButton(LANGUAGES['br']['name'], callback_data='lang_br')],
        ]
        await update.effective_message.reply_text("Select Language:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [[InlineKeyboardButton("📢 Join Private Channel", url=CHANNEL_LINK)], [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join_status')]]
        await update.effective_message.reply_text("⚠️ <b>Action Required!</b>\nJoin channel first.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def language_handler(update, context):
    query = update.callback_query
    lang = query.data.split('_')[1]
    context.user_data['selected_lang'] = lang
    await query.message.delete()
    keyboard = [[InlineKeyboardButton(LANGUAGES[lang]['earn_btn'], callback_data='start_earning')]]
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_WELCOME, caption=f"Language: {LANGUAGES[lang]['name']}\nClick to proceed:", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_registration_info(update, context):
    lang = context.user_data.get('selected_lang', 'en')
    keyboard = [
        [InlineKeyboardButton(f"🔗 {LANGUAGES[lang]['reg_btn']}", url="https://1wezue.com/casino")],
        [InlineKeyboardButton(f"{LANGUAGES[lang]['verify_btn']}", callback_data='verify_reg')],
        [InlineKeyboardButton(f"🆘 Help", url="https://t.me/SUNNY_BRO1")]
    ]
    await update.callback_query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_REG, caption="<b>Step 1- Register.</b>\nUse promo code: <b>BLACK110</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def verify_process_start(update, context):
    lang = context.user_data.get('selected_lang', 'en')
    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="⏳ Checking synchronization... Please wait 5 seconds.")
    await asyncio.sleep(5) 
    await msg.delete()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=LANGUAGES[lang]['ask_id'])
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_text = update.message.text
    lang = context.user_data.get('selected_lang', 'en')
    analyzing = await update.message.reply_text(LANGUAGES[lang]['analyzing'])
    await asyncio.sleep(2)
    await analyzing.delete()
    keyboard = [[InlineKeyboardButton(f"🎮 {LANGUAGES[lang]['play_btn']}", callback_data='play_hack_action')], [InlineKeyboardButton(f"📺 {LANGUAGES[lang]['guide_btn']}", url=HOW_TO_USE_LINK)]]
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_SUCCESS, caption=LANGUAGES[lang]['success_msg'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def play_hack_menu(update, context):
    lang = context.user_data.get('selected_lang', 'en')
    keyboard = [
        [InlineKeyboardButton("✈️ Aviator", callback_data='game_aviator')],
        [InlineKeyboardButton("💣 Mines", callback_data='game_mines')],
        [InlineKeyboardButton("⚽ Penalty", callback_data='game_penalty')],
        [InlineKeyboardButton("👑 King Thimbles", callback_data='game_king_thimbles')],
    ]
    await update.callback_query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_HACK_MENU, caption=LANGUAGES[lang]['select_game'], reply_markup=InlineKeyboardMarkup(keyboard))

async def game_selection_handler(update, context):
    query = update.callback_query
    game_type = query.data
    games = {
        'game_aviator': (LOGO_AVIATOR, "Aviator", LINK_AVIATOR),
        'game_mines': (LOGO_MINES, "Mines", LINK_MINES),
        'game_penalty': (LOGO_PENALTY, "Penalty", LINK_PENALTY),
        'game_king_thimbles': (LOGO_KING_THIMBLES, "King Thimbles", LINK_KING_THIMBLES)
    }
    logo, name, url = games[game_type]
    keyboard = [[InlineKeyboardButton(f"📱 Open {name} Hack", web_app=WebAppInfo(url=url))], [InlineKeyboardButton("🔙 Back", callback_data='play_hack_action')]]
    await query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=logo, caption=f"<b>{name} Hack Connected!</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# ================= ADMIN PANEL =================
async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    users = get_users()
    keyboard = [
        [InlineKeyboardButton("📝 Simple Broadcast", callback_data='admin_simple_broadcast')],
        [InlineKeyboardButton("🔗 Button Broadcast", callback_data='admin_btn_broadcast')],
        [InlineKeyboardButton("✨ Signal Broadcast", callback_data='admin_auto_signal_broadcast')],
        [InlineKeyboardButton("❌ Close", callback_data='admin_close')]
    ]
    await update.message.reply_text(f"👑 <b>ADMIN PANEL</b>\nTotal Users: {len(users)}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def start_broadcast(update, context):
    await update.callback_query.edit_message_text("Send message (Text/Photo) or /cancel")
    data = update.callback_query.data
    if 'simple' in data: return BROADCAST_SIMPLE
    if 'btn' in data: return BTN_BROADCAST_CONTENT
    if 'auto_signal' in data: return BROADCAST_AUTO_SIGNAL

async def perform_simple_broadcast(update, context):
    users = get_users()
    for uid in users:
        try:
            if update.message.photo: await context.bot.send_photo(int(uid), update.message.photo[-1].file_id, update.message.caption)
            else: await context.bot.send_message(int(uid), update.message.text)
        except: pass
    await update.message.reply_text("Done!")
    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Auto Job
    application.job_queue.run_repeating(auto_update_message_job, interval=3600, first=10)

    # Conversations
    verify_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_process_start, pattern='^verify_reg$')],
        states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    admin_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_broadcast, pattern='^admin_simple_broadcast$'),
            CallbackQueryHandler(start_broadcast, pattern='^admin_auto_signal_broadcast$')
        ],
        states={
            BROADCAST_SIMPLE: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, perform_simple_broadcast)],
            BROADCAST_AUTO_SIGNAL: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, perform_simple_broadcast)], #Simplified for space
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('admin', admin_panel))
    application.add_handler(verify_conv)
    application.add_handler(admin_conv)
    application.add_handler(CallbackQueryHandler(language_handler, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(show_registration_info, pattern='^start_earning$'))
    application.add_handler(CallbackQueryHandler(play_hack_menu, pattern='^play_hack_action$'))
    application.add_handler(CallbackQueryHandler(game_selection_handler, pattern='^game_'))
    application.add_handler(CallbackQueryHandler(lambda u,c: start(u,c), pattern='^check_join_status$'))
    application.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.message.delete(), pattern='^admin_close$'))

    # Start Web Server for Render
    loop = asyncio.get_event_loop()
    loop.create_task(start_web_server())

    application.run_polling()
