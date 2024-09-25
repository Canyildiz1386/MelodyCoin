from telegram import Update
from telegram.ext import Application, CommandHandler

async def start(update: Update, context):
    await update.message.reply_text("Here is a useful link: https://351d-81-215-194-167.ngrok-free.app")

def main():
    application = Application.builder().token('7476580536:AAFhZS6bM63fWJcSyPn0KfFNpWT5Jh5t4vE').build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == '__main__':
    main()
