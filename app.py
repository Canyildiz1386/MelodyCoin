import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

user_data = {}
products = {
    1: {'name': '🎮 Game A', 'price': 10},
    2: {'name': '🎮 Game B', 'price': 15},
}
orders = {}
TELEGRAM_TOKEN = "7476580536:AAFhZS6bM63fWJcSyPn0KfFNpWT5Jh5t4vE"
STEAM_API_KEY = "your_steam_api_key"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🛒 View Products", callback_data='view_products')],
        [InlineKeyboardButton("💰 Check Wallet", callback_data='check_wallet')],
        [InlineKeyboardButton("📦 Order Status", callback_data='order_status')],
        [InlineKeyboardButton("🔍 Steam Game Info", callback_data='steam_game_info')],
        [InlineKeyboardButton("📱 Verify Mobile Number", callback_data='verify_mobile')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Welcome to the SteamBot! 🎉 Choose an option below: 👇", reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text("Welcome to the SteamBot! 🎉 Choose an option below: 👇", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith('buy_'):
        product_id = int(query.data.split('_')[1])
        await buy_product(query, product_id)
    elif query.data == 'view_products':
        await show_products(query)
    elif query.data == 'check_wallet':
        await show_wallet(query)
    elif query.data == 'order_status':
        await show_order_status(query)
    elif query.data == 'steam_game_info':
        await request_steam_game_info(query)
    elif query.data == 'verify_mobile':
        await verify_mobile(query)
    elif query.data == 'main_menu':
        await start(query, context)


async def show_products(query):
    keyboard = [
        [InlineKeyboardButton(f"{info['name']} - 💵 ${info['price']}", callback_data=f"buy_{pid}")]
        for pid, info in products.items()
    ]
    # Adding the Back button
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🛍️ Available Products:", reply_markup=reply_markup)


async def show_wallet(query):
    user_id = query.from_user.id
    balance = user_data.get(user_id, {}).get('wallet', 0)
    # Adding the Back button
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"💼 Your Current Wallet Balance: ${balance}", reply_markup=reply_markup)


async def show_order_status(query):
    user_id = query.from_user.id
    user_orders = orders.get(user_id, {})
    if user_orders:
        status_list = "\n".join([f"📦 Order {oid}: {status}" for oid, status in user_orders.items()])
        # Adding the Back button
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"📝 Your Orders:\n{status_list}", reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("❌ You have no orders.", reply_markup=reply_markup)


async def buy_product(query, product_id):
    user_id = query.from_user.id
    product = products[product_id]
    user_balance = user_data.get(user_id, {}).get('wallet', 0)

    if user_balance >= product['price']:
        user_data[user_id]['wallet'] -= product['price']
        orders.setdefault(user_id, {})[product_id] = "Purchased"
        # Adding the Back button
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"✅ You have purchased {product['name']} for ${product['price']}! Remaining balance: ${user_data[user_id]['wallet']}", reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("⚠️ Insufficient funds. Please add more money to your wallet!", reply_markup=reply_markup)


async def verify_mobile(query):
    await query.edit_message_text("🔒 Please share your mobile number:")
    keyboard = [[KeyboardButton("📲 Share Contact", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await query.message.reply_text("Click the button below to verify your mobile number:", reply_markup=reply_markup)


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    contact = update.message.contact
    if contact is not None:
        user_data[contact.user_id] = {"phone_number": contact.phone_number}
        await update.message.reply_text(f"✅ Mobile number {contact.phone_number} verified successfully!")
    else:
        await update.message.reply_text("❌ Failed to verify your mobile number.")


async def request_steam_game_info(query):
    # Adding the Back button
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🔍 Please enter the Steam App ID of the game you want to inquire about:", reply_markup=reply_markup)


async def steam_game_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    app_id = update.message.text
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&key={STEAM_API_KEY}"
    response = requests.get(url).json()

    if app_id in response and response[app_id]['success']:
        game_info = response[app_id]['data']
        game_name = game_info['name']
        game_price = game_info['price_overview']['final_formatted'] if 'price_overview' in game_info else 'Free'
        await update.message.reply_text(f"🎮 {game_name} - 💵 {game_price}")
    else:
        await update.message.reply_text("❌ Invalid game ID or no data available.")


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, steam_game_info))

    application.run_polling()


if __name__ == '__main__':
    main()
