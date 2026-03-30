import logging
import asyncio
import os
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

# --- MEDIA LINKS (FIXED URLS) ---
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

LOGO_AVIATOR = "https://i.ibb.co/PZBBDv85/images-9.jpg"
LOGO_MINES = "https://i.ibb.co/MDVxth7x/images-8.jpg"
LOGO_PENALTY = "https://i.ibb.co/5WzBdWX4/hqdefault.jpg"
LOGO_KING_THIMBLES = "https://i.ibb.co/8LYwvg1j/maxresdefault.jpg"

# --- HACK LINKS ---
LINK_AVIATOR = "https://aviatorbahohacker.fwh.is/"
LINK_MINES = "https://mines-game-hack.netlify.app/"
LINK_PENALTY = "https://pnalteaybot.netlify.app/"
LINK_KING_THIMBLES = "https://kingthimblesbot.netlify.app/"

HOW_TO_USE_LINK = "https://youtube.com/@sunny_bro11?si=gYfOtXnKayCkZloF"

# --- FILES ---
USER_FILE = "users.txt"

# --- CONVERSATION STATES ---
WAITING_FOR_ID = 0
(
    BROADCAST_SIMPLE,
    BTN_BROADCAST_CONTENT,
    BTN_BROADCAST_LABEL,
    BTN_BROADCAST_LINK,
    BROADCAST_AUTO_SIGNAL
) = range(2, 7)

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
def save_user(user_id):
    users = get_users()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

# ================= UTILITY FUNCTIONS =================
async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except BadRequest:
        logging.error("Bot is not admin in the channel or ID is wrong!")
        return False
    except Exception as e:
        logging.error(f"Error checking membership: {e}")
        return False

async def send_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"Hello {user.first_name}, Welcome!\nPlease select your language:"

    keyboard = [
        [InlineKeyboardButton(LANGUAGES['en']['name'], callback_data='lang_en'),
         InlineKeyboardButton(LANGUAGES['hi']['name'], callback_data='lang_hi')],
        [InlineKeyboardButton(LANGUAGES['pk']['name'], callback_data='lang_pk'),
         InlineKeyboardButton(LANGUAGES['bd']['name'], callback_data='lang_bd')],
        [InlineKeyboardButton(LANGUAGES['id']['name'], callback_data='lang_id'),
         InlineKeyboardButton(LANGUAGES['ru']['name'], callback_data='lang_ru')],
        [InlineKeyboardButton(LANGUAGES['tr']['name'], callback_data='lang_tr'),
         InlineKeyboardButton(LANGUAGES['br']['name'], callback_data='lang_br')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.delete()
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=welcome_text, 
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=welcome_text, 
            reply_markup=reply_markup
        )

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
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
            chat_id=user_id, 
            text=join_text, 
            reply_markup=InlineKeyboardMarkup(keyboard), 
            parse_mode='HTML'
        )
    return ConversationHandler.END

async def restart_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

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
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=IMAGE_URL_WELCOME,
            caption=f"Language: {lang_data['name']}\n\nClick below to proceed:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Photo send failed: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Click below to start:",
            reply_markup=reply_markup
        )
    return ConversationHandler.END

async def show_registration_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    info_text = (
        "<b>Step 1- Register.</b>\n\n"
        "To synchronize with the bot, you need to create a new account strictly via the link from the bot "
        "and use the promo code <b>BLACK110</b>\n\n"
        "If you opened the link and accessed an old account, you need to:\n"
        "- Log out of the old account\n"
        "- Close the website\n"
        "- Reopen the link from the bot's button\n\n"
        "<b>2- Complete the registration</b>\n\n"
        "After successful registration, click the <b>Verify</b> button below."
    )

    keyboard = [
        [InlineKeyboardButton(f"🔗 {lang_data['reg_btn']}", url="https://1wezue.com/casino")],
        [InlineKeyboardButton(f"{lang_data['verify_btn']}", callback_data='verify_reg')],
        [InlineKeyboardButton(f"🆘 {lang_data['help_btn']}", url="https://t.me/SUNNY_BRO1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=IMAGE_URL_REG,
        caption=info_text,
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def verify_process_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    msg = await context.bot.send_message(
        chat_id=chat_id, 
        text="⏳ Checking synchronization... Please wait 15 seconds."
    )
    await asyncio.sleep(15) 
    
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    except: pass

    await context.bot.send_message(
        chat_id=chat_id, 
        text=lang_data['ask_id']
    )
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_text = update.message.text.strip()
    context.user_data['user_provided_id'] = user_id_text
    
    user = update.effective_user
    chat_id = update.effective_chat.id
    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    analyzing_msg = await update.message.reply_text(f"⏳ {lang_data['analyzing']}")

    admin_text = (
        f"🚨 <b>New Auto-Verified User!</b>\n"
        f"👤 Name: {user.first_name}\n"
        f"🆔 Telegram ID: {user.id}\n"
        f"📝 <b>1Win ID:</b> <code>{user_id_text}</code>\n"
        f"✅ <i>Bot has auto-approved this user.</i>"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID, 
            text=admin_text, 
            parse_mode='HTML'
        )
    except Exception as e:
        logging.error(f"Admin notification failed: {e}")

    await asyncio.sleep(2)
    
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=analyzing_msg.message_id)
    except: pass

    final_keyboard = [
        [InlineKeyboardButton(f"🎮 {lang_data['play_btn']}", callback_data='play_hack_action')],
        [InlineKeyboardButton(f"📺 {lang_data['guide_btn']}", url=HOW_TO_USE_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(final_keyboard)

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=IMAGE_URL_SUCCESS,
        caption=lang_data['success_msg'],
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def play_hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    keyboard = [
        [InlineKeyboardButton("✈️ Aviator", callback_data='game_aviator')],
        [InlineKeyboardButton("💣 Mines", callback_data='game_mines')],
        [InlineKeyboardButton("⚽ Penalty", callback_data='game_penalty')],
        [InlineKeyboardButton("👑 King Thimbles", callback_data='game_king_thimbles')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=IMAGE_URL_HACK_MENU,
        caption=lang_data['select_game'],
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def game_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    game_type = query.data
    logo_url = LOGO_AVIATOR
    game_name = "Aviator"
    hack_url = LINK_AVIATOR

    if game_type == 'game_aviator':
        logo_url = LOGO_AVIATOR
        game_name = "Aviator"
        hack_url = LINK_AVIATOR
    elif game_type == 'game_mines':
        logo_url = LOGO_MINES
        game_name = "Mines"
        hack_url = LINK_MINES
    elif game_type == 'game_penalty':
        logo_url = LOGO_PENALTY
        game_name = "Penalty"
        hack_url = LINK_PENALTY
    elif game_type == 'game_king_thimbles':
        logo_url = LOGO_KING_THIMBLES
        game_name = "King Thimbles"
        hack_url = LINK_KING_THIMBLES

    keyboard = [
        [InlineKeyboardButton(f"📱 Open {game_name} Hack", web_app=WebAppInfo(url=hack_url))],
        [InlineKeyboardButton("🔙 Back", callback_data='play_hack_action')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.delete()
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=logo_url,
            caption=f"<b>{game_name} Hack Connected!</b>\n\nClick the button below to access the hack tool.",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Game photo failed: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"<b>{game_name} Selected.</b>\nClick below:",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

# ================= ADMIN HANDLERS =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END # Breaks any stuck states

    users = get_users()
    msg = (
        f"👑 <b>ADMIN PANEL</b> 👑\n\n"
        f"👥 <b>Total Users:</b> {len(users)}\n"
        f"Choose an option below:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📝 Plain Broadcast", callback_data='admin_simple_broadcast')],
        [InlineKeyboardButton("🔗 Custom Button Broadcast", callback_data='admin_btn_broadcast')],
        [InlineKeyboardButton("✨ Signal Broadcast (Auto Button)", callback_data='admin_auto_signal_broadcast')],
        [InlineKeyboardButton("❌ Close", callback_data='admin_close')]
    ]
    await update.message.reply_text(
        msg, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode='HTML'
    )
    return ConversationHandler.END

async def start_simple_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(
        "📝 <b>Plain Broadcast Mode</b>\n\nSend message (Text or Photo).\nType /cancel to cancel.", 
        parse_mode='HTML'
    )
    return BROADCAST_SIMPLE

async def perform_simple_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_users()
    count = 0
    status_msg = await update.message.reply_text(f"🚀 Sending Plain Broadcast to {len(users)} users...")
    
    for uid in users:
        try:
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=int(uid), 
                    photo=update.message.photo[-1].file_id, 
                    caption=update.message.caption
                )
            else:
                await context.bot.send_message(
                    chat_id=int(uid), 
                    text=update.message.text
                )
            count += 1
        except Exception as e:
            logging.warning(f"Broadcast failed for {uid}: {e}")
        await asyncio.sleep(0.05)
        
    await status_msg.edit_text(f"✅ Plain Broadcast Sent to {count} users.")
    return ConversationHandler.END

async def start_btn_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(
        "🔗 <b>Custom Button Broadcast</b>\n\nStep 1: Send Message Content.\nType /cancel to cancel.", 
        parse_mode='HTML'
    )
    return BTN_BROADCAST_CONTENT

async def get_btn_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['bc_type'] = 'photo'
        context.user_data['bc_photo'] = update.message.photo[-1].file_id
        context.user_data['bc_caption'] = update.message.caption
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
    
    # Validating URL Scheme to avoid BadRequest
    if not link.startswith(('http://', 'https://')):
        link = 'https://' + link

    label = context.user_data['bc_btn_label']
    keyboard = [[InlineKeyboardButton(label, url=link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    users = get_users()
    count = 0
    status_msg = await update.message.reply_text(f"🚀 Sending Custom Button Broadcast to {len(users)} users...")

    for uid in users:
        try:
            if context.user_data['bc_type'] == 'photo':
                await context.bot.send_photo(
                    chat_id=int(uid), 
                    photo=context.user_data['bc_photo'], 
                    caption=context.user_data['bc_caption'], 
                    reply_markup=reply_markup
                )
            else:
                await context.bot.send_message(
                    chat_id=int(uid), 
                    text=context.user_data['bc_text'], 
                    reply_markup=reply_markup
                )
            count += 1
        except Exception as e:
            logging.warning(f"Button broadcast failed for {uid}: {e}")
        await asyncio.sleep(0.05)
    await status_msg.edit_text(f"✅ Custom Button Broadcast Sent to {count} users.")
    return ConversationHandler.END

async def start_auto_signal_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(
        "✨ <b>Signal Broadcast Mode</b>\n\nSend message (Text or Photo).\n'GET SIGNAL✨' button will be added automatically.\nType /cancel to cancel.", 
        parse_mode='HTML'
    )
    return BROADCAST_AUTO_SIGNAL

async def perform_auto_signal_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_users()
    count = 0
    status_msg = await update.message.reply_text(f"🚀 Sending Signal Broadcast to {len(users)} users...")
    
    auto_keyboard = [[InlineKeyboardButton("GET SIGNAL✨", callback_data='restart_bot_action')]]
    auto_markup = InlineKeyboardMarkup(auto_keyboard)

    for uid in users:
        try:
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=int(uid), 
                    photo=update.message.photo[-1].file_id, 
                    caption=update.message.caption, 
                    reply_markup=auto_markup
                )
            else:
                await context.bot.send_message(
                    chat_id=int(uid), 
                    text=update.message.text, 
                    reply_markup=auto_markup
                )
            count += 1
        except Exception as e:
            logging.warning(f"Signal broadcast failed for {uid}: {e}")
        await asyncio.sleep(0.05)
        
    await status_msg.edit_text(f"✅ Signal Broadcast Sent to {count} users.")
    return ConversationHandler.END

async def close_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Admin Panel Closed")
    try:
        await update.callback_query.message.delete()
    except Exception:
        pass

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
    
    if not os.path.exists(USER_FILE):
        open(USER_FILE, 'w').close()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    verify_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_process_start, pattern='^verify_reg$')],
        states={
            WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)],
        },
        # Added /admin as fallback to ensure admins don't get stuck in ID verification logic
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('admin', admin_panel)]
    )

    admin_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_simple_broadcast, pattern='^admin_simple_broadcast$'),
            CallbackQueryHandler(start_btn_broadcast, pattern='^admin_btn_broadcast$'),
            CallbackQueryHandler(start_auto_signal_broadcast, pattern='^admin_auto_signal_broadcast$')
        ],
        states={
            # Excluded ~filters.COMMAND here so typing /cancel actually aborts the broadcast
            BROADCAST_SIMPLE: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, perform_simple_broadcast)],
            BTN_BROADCAST_CONTENT: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, get_btn_content)],
            BTN_BROADCAST_LABEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_btn_label)],
            BTN_BROADCAST_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, perform_btn_broadcast)],
            BROADCAST_AUTO_SIGNAL: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, perform_auto_signal_broadcast)],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('admin', admin_panel)]
    )

    # Adding Conversations FIRST to prevent normal handlers from overlapping
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

    logging.info("Bot is running...")
    application.run_polling()