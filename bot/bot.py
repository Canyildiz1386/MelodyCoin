import hmac
import hashlib
from telegram import Update
from telegram.ext import Application, CommandHandler

BOT_TOKEN = '7476580536:AAFhZS6bM63fWJcSyPn0KfFNpWT5Jh5t4vE'
SECRET_KEY = "your_secret_key"

def generate_hash(user_id, username):
    data = f"user_id={user_id}&username={username}"
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()

async def start(update: Update, context):
    user = update.message.from_user
    user_id = user.id
    username = user.username
    user_hash = generate_hash(user_id, username)
    url = f"https://d665-37-27-40-154.ngrok-free.app/?user_id={user_id}&username={username}&hash={user_hash}"
    await update.message.reply_text(f"Here is your personalized link: {url}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == '__main__':
    main()
