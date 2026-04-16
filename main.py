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
from telegram.error import BadRequest

================= CONFIGURATION =================

BOT_TOKEN = os.getenv("BOT_TOKEN", "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1146186608"))
REQUIRED_CHANNEL = int(os.getenv("REQUIRED_CHANNEL", "-1001481593780"))
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

--- MEDIA LINKS ---

IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

LOGO_AVIATOR = "https://i.ibb.co/PZBBDv85/images-9.jpg"
LOGO_MINES = "https://i.ibb.co/MDVxth7x/images-8.jpg"
LOGO_PENALTY = "https://i.ibb.co/5WzBdWX4/hqdefault.jpg"
LOGO_KING_THIMBLES = "https://i.ibb.co/8LYwvg1j/maxresdefault.jpg"

--- HACK LINKS ---

LINK_AVIATOR = "https://aviatorbahohacker.fwh.is/"
LINK_MINES = "https://mines-game-hack.netlify.app/"
LINK_PENALTY = "https://pnalteaybot.netlify.app/"
LINK_KING_THIMBLES = "https://kingthimblesbot.netlify.app/"

HOW_TO_USE_LINK = "https://youtube.com/@sunny_bro11?si=gYfOtXnKayCkZloF"

--- FILES ---

USER_FILE = "users.txt"

--- CONVERSATION STATES ---

WAITING_FOR_ID = 0
(
BROADCAST_SIMPLE,
BTN_BROADCAST_CONTENT,
BTN_BROADCAST_LABEL,
BTN_BROADCAST_STYLE, # নতুন স্টেট: স্টাইলের জন্য
BTN_BROADCAST_LINK,
BROADCAST_AUTO_SIGNAL
) = range(2, 8)

--- LANGUAGE CONFIG ---

LANGUAGES = {
'en': {'name': '🇺🇸 English', 'earn_btn': 'Start Earning Money', 'reg_btn': 'Registration Link', 'verify_btn': '✅ I have Registered (Verify)', 'ask_id': 'Please send your 9-digit Account ID:', 'analyzing': '🔄 Verifying your ID...', 'success_msg': '✅ <b>ACCOUNT VERIFIED!</b>\n\nYour account has been successfully synchronized.', 'play_btn': 'Play With Hack', 'guide_btn': 'How to use', 'help_btn': 'Help', 'select_game': 'Select a game to start hacking:'},
'bd': {'name': '🇧🇩 Bangladesh (Bangla)', 'earn_btn': 'টাকা আয় শুরু করুন', 'reg_btn': 'রেজিস্ট্রেশন লিংক', 'verify_btn': '✅ আমার রেজিস্ট্রেশন সম্পন্ন হয়েছে', 'ask_id': 'অনুগ্রহ করে আপনার ৯ ডিজিটের একাউন্ট আইডি দিন:', 'analyzing': '🔄 আপনার আইডি যাচাই করা হচ্ছে...', 'success_msg': '✅ <b>একাউন্ট ভেরিফাইড!</b>\n\nআপনার একাউন্টটি সফলভাবে বটের সাথে যুক্ত হয়েছে।', 'play_btn': 'Play With Hack', 'guide_btn': 'কিভাবে ব্যবহার করবেন', 'help_btn': 'সাহায্য', 'select_game': 'হ্যাক শুরু করতে একটি গেম সিলেক্ট করুন:'},
# অন্য ল্যাঙ্গুয়েজগুলো আগের কোড থেকে একইভাবে থাকবে...
}

================= DATABASE FUNCTIONS =================

def save_user(user_id):
users = get_users()
if str(user_id) not in users:
with open(USER_FILE, "a") as f:
f.write(f"{user_id}\n")

def get_users():
if not os.path.exists(USER_FILE):
return []
with open(USER_FILE, "r") as f:
return [line.strip() for line in f.readlines() if line.strip()]

================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
save_user(user_id)

code
Code
download
content_copy
expand_less
# মেম্বারশিপ চেক
try:
    member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
    is_member = member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
except:
    is_member = False

if is_member:
    # ল্যাঙ্গুয়েজ মেনু পাঠানো (আগের কোডের মতো)
    keyboard = [
        [InlineKeyboardButton(LANGUAGES['en']['name'], callback_data='lang_en'),
         InlineKeyboardButton(LANGUAGES['bd']['name'], callback_data='lang_bd')],
    ]
    await context.bot.send_message(chat_id=user_id, text="Please select your language:", reply_markup=InlineKeyboardMarkup(keyboard))
else:
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join_status')]
    ]
    await context.bot.send_message(chat_id=user_id, text="⚠️ Join our channel first!", reply_markup=InlineKeyboardMarkup(keyboard))

async def verify_process_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

code
Code
download
content_copy
expand_less
chat_id = update.effective_chat.id
lang_code = context.user_data.get('selected_lang', 'en')

# ১৫ সেকেন্ড থেকে কমিয়ে ৫ সেকেন্ড করা হয়েছে
msg = await context.bot.send_message(chat_id=chat_id, text="⏳ Checking synchronization... Please wait 5 seconds.")
await asyncio.sleep(5) 

try: await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
except: pass

await context.bot.send_message(chat_id=chat_id, text=LANGUAGES.get(lang_code, LANGUAGES['en'])['ask_id'])
return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id_text = update.message.text.strip()
lang_code = context.user_data.get('selected_lang', 'en')
lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

code
Code
download
content_copy
expand_less
analyzing_msg = await update.message.reply_text(f"⏳ {lang_data['analyzing']}")

# অ্যাডমিনকে নোটিফিকেশন পাঠানো
admin_text = f"🚨 <b>New User Verified!</b>\nID: <code>{user_id_text}</code>\nTG ID: {update.effective_user.id}"
await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode='HTML')

await asyncio.sleep(2)
await analyzing_msg.delete()

keyboard = [[InlineKeyboardButton(f"🎮 {lang_data['play_btn']}", callback_data='play_hack_action')]]
await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_SUCCESS, caption=lang_data['success_msg'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
return ConversationHandler.END
================= PROFESSIONAL ADMIN PANEL =================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
if update.effective_user.id != ADMIN_ID:
return ConversationHandler.END

code
Code
download
content_copy
expand_less
users = get_users()
msg = (
    f"🛠 <b>PROFESSIONAL ADMIN PANEL</b>\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"👥 <b>Total Users:</b> <code>{len(users)}</code>\n"
    f"🤖 <b>Bot Status:</b> 🟢 Online\n"
    f"━━━━━━━━━━━━━━━━━━━━\n"
    f"নিচের যেকোনো অপশন সিলেক্ট করুন:"
)

keyboard = [
    [InlineKeyboardButton("📝 Plain Broadcast", callback_data='admin_simple_broadcast')],
    [InlineKeyboardButton("🔗 Button Broadcast", callback_data='admin_btn_broadcast')],
    [InlineKeyboardButton("✨ Signal (Auto Button)", callback_data='admin_auto_signal_broadcast')],
    [InlineKeyboardButton("🔄 Refresh Stats", callback_data='admin_refresh'), InlineKeyboardButton("❌ Close", callback_data='admin_close')]
]

if update.callback_query:
    await update.callback_query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
else:
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
return ConversationHandler.END
--- Custom Button Broadcast with Style (Coloring) ---

async def start_btn_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.callback_query.answer()
await update.callback_query.message.edit_text("🔗 <b>Step 1:</b> Send Message Content (Text or Photo):", parse_mode='HTML')
return BTN_BROADCAST_CONTENT

async def get_btn_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
if update.message.photo:
context.user_data['bc_type'] = 'photo'
context.user_data['bc_photo'] = update.message.photo[-1].file_id
context.user_data['bc_caption'] = update.message.caption
else:
context.user_data['bc_type'] = 'text'
context.user_data['bc_text'] = update.message.text
await update.message.reply_text("🔗 <b>Step 2:</b> Enter Button Name:")
return BTN_BROADCAST_LABEL

async def get_btn_label(update: Update, context: ContextTypes.DEFAULT_TYPE):
context.user_data['temp_label'] = update.message.text
# স্টাইল বা কালার পছন্দ করা
keyboard = [
[InlineKeyboardButton("🟢 Success Style", callback_data='style_green')],
[InlineKeyboardButton("🔴 Alert Style", callback_data='style_red')],
[InlineKeyboardButton("💎 Premium Style", callback_data='style_blue')],
[InlineKeyboardButton("✨ Glow Style", callback_data='style_gold')],
[InlineKeyboardButton("⚪ Plain Style", callback_data='style_none')]
]
await update.message.reply_text("🎨 <b>Step 3:</b> Choose Button Style (Emoji Theme):", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
return BTN_BROADCAST_STYLE

async def get_btn_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
style = query.data.split('_')[1]
label = context.user_data['temp_label']

code
Code
download
content_copy
expand_less
if style == 'green': final_label = f"🟢 {label} 🟢"
elif style == 'red': final_label = f"🔴 {label} 🔴"
elif style == 'blue': final_label = f"💎 {label} 💎"
elif style == 'gold': final_label = f"✨ {label} ✨"
else: final_label = label

context.user_data['bc_btn_label'] = final_label
await query.message.edit_text(f"Style: {style.upper()}\n🔗 <b>Step 4:</b> Enter Button URL:")
return BTN_BROADCAST_LINK
--- ব্রডকাস্ট সম্পন্ন করা ---

async def perform_btn_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
link = update.message.text.strip()
label = context.user_data['bc_btn_label']
keyboard = [[InlineKeyboardButton(label, url=link)]]

code
Code
download
content_copy
expand_less
users = get_users()
count = 0
for uid in users:
    try:
        if context.user_data['bc_type'] == 'photo':
            await context.bot.send_photo(chat_id=int(uid), photo=context.user_data['bc_photo'], caption=context.user_data['bc_caption'], reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await context.bot.send_message(chat_id=int(uid), text=context.user_data['bc_text'], reply_markup=InlineKeyboardMarkup(keyboard))
        count += 1
        await asyncio.sleep(0.05)
    except: continue

await update.message.reply_text(f"✅ Broadcast sent to {count} users.")
return ConversationHandler.END
================= MAIN =================

if name == 'main':
if not os.path.exists(USER_FILE): open(USER_FILE, 'w').close()
application = ApplicationBuilder().token(BOT_TOKEN).build()

code
Code
download
content_copy
expand_less
# অ্যাডমিন কনভারসেশন
admin_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_btn_broadcast, pattern='^admin_btn_broadcast$'),
        # অন্য ব্রডকাস্টগুলো এখানে একইভাবে যোগ হবে...
    ],
    states={
        BTN_BROADCAST_CONTENT: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, get_btn_content)],
        BTN_BROADCAST_LABEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_btn_label)],
        BTN_BROADCAST_STYLE: [CallbackQueryHandler(get_btn_style, pattern='^style_')],
        BTN_BROADCAST_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, perform_btn_broadcast)],
    },
    fallbacks=[CommandHandler('cancel', admin_panel)]
)

# আইডি ভেরিফাই কনভারসেশন
verify_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(verify_process_start, pattern='^verify_reg$')],
    states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
    fallbacks=[CommandHandler('cancel', start)]
)

application.add_handler(admin_conv)
application.add_handler(verify_conv)
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('admin', admin_panel))
application.add_handler(CallbackQueryHandler(admin_panel, pattern='^admin_refresh$'))
# ... অন্যান্য কলব্যাক হ্যান্ডলার ...

print("Bot is running...")
application.run_polling()

