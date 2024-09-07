from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler
import os
import requests

BOT_TOKEN = "6837318452:AAFNfVxHrCCzYT1qTg9fmlNuMTTYBthW0Is"
WEB_APP_URL = "https://1919-78-182-185-235.ngrok-free.app/nickname"

async def start(update: Update, context):
    args = context.args
    referrer_id = args[0] if args else None  # Referral ID if provided
    user = update.message.from_user
    tg_id = user.id
    username = user.username
    web_app_url = f"{WEB_APP_URL}?tg_id={tg_id}&username={username}&referrer_id={referrer_id}"

    welcome_image_path = "app/static/img/_f3aced6d-129f-4ffe-9077-3f35cb33f860.jpeg"
    print(update.effective_user.username)
    print(update.effective_user.id)

    try:
        fd = os.open(welcome_image_path, os.O_RDONLY) 
        with os.fdopen(fd, 'rb') as img_file: 
            await context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=img_file,
                caption="🎉 Welcome to the Bot! 🎉\nWe're excited to have you here! 🌟"
            )
    except Exception as e:
        await update.message.reply_text(f"Failed to send image. Error: {str(e)}")

    welcome_message = (
        "🎉✨ Welcome to the best bot experience! ✨🎉\n\n"
        "💬 Start exploring our features and have fun! 🚀\n"
        "🧑‍💻 Here's what you can do: 🔍\n"
        "1️⃣ Get access to our mini app by clicking the button below! 🖱️👇\n"
        "2️⃣ Invite your friends and get rewards! 🎁👥\n"
        "3️⃣ Enjoy new features and updates every week! 🌈📅\n\n"
        "🎈 Have a great time! 🎈"
    )

    keyboard = [
        [InlineKeyboardButton("🚀 Open Mini App 🚀", url=web_app_url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=welcome_message,
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.run_polling()
