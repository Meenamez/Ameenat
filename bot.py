import os
import random
import string
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from flask import Flask

# Flask app for Render health checks
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

# Initialize bot
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 5000))

# Store trading status per user
user_trading_status = {}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Generate random deposit address
def generate_deposit_address():
    chars = string.ascii_letters + string.digits
    return '0x' + ''.join(random.choice(chars) for _ in range(40))

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Deposit", callback_data='deposit')],
        [InlineKeyboardButton("📈 Trade", callback_data='trade')],
        [InlineKeyboardButton("⏯️ Stop/Start", callback_data='toggle_trade')],
        [InlineKeyboardButton("💸 Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("📊 Status", callback_data='status')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🚀 Welcome to Demo Trading Bot!\n\n"
        "Choose an option below:",
        reply_markup=reply_markup
    )

# Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == 'deposit':
        deposit_address = generate_deposit_address()
        await query.edit_message_text(
            f"💰 **Deposit ETH Here:**\n\n"
            f"`{deposit_address}`\n\n"
            f"Send ETH to this address to fund your demo account.\n"
            f"Demo balance: 100 ETH (for testing)",
            parse_mode='Markdown'
        )
    
    elif query.data == 'trade':
        profit_loss = random.uniform(-5, 15)
        if profit_loss >= 0:
            message = f"📈 **Trade Executed!**\n\n✅ Profit: +{profit_loss:.2f} ETH\n\nKeep trading!"
        else:
            message = f"📉 **Trade Executed!**\n\n⚠️ Loss: {profit_loss:.2f} ETH\n\nBetter luck next time!"
        
        await query.edit_message_text(
            f"🚀 **Hurry! I'm going into the ETH market now to make profit for you!**\n\n"
            f"{message}",
            parse_mode='Markdown'
        )
    
    elif query.data == 'toggle_trade':
        if user_id not in user_trading_status:
            user_trading_status[user_id] = True
        
        user_trading_status[user_id] = not user_trading_status[user_id]
        status = "✅ STARTED" if user_trading_status[user_id] else "⛔ STOPPED"
        
        await query.edit_message_text(
            f"🔄 **Trading Status Changed**\n\n"
            f"Trading is now: **{status}**\n\n"
            f"Your demo trades will {'now be executed' if user_trading_status[user_id] else 'be paused'}."
        )
    
    elif query.data == 'withdraw':
        # Store that we're waiting for ETH address
        context.user_data['awaiting_address'] = True
        await query.edit_message_text(
            "💸 **Withdraw Profits**\n\n"
            "Please send your ETH address where you want to receive 10 ETH profit.\n\n"
            "Format: `0xYourEthereumAddressHere`",
            parse_mode='Markdown'
        )
    
    elif query.data == 'status':
        trading_active = user_trading_status.get(user_id, False)
        status = "🟢 ACTIVE" if trading_active else "🔴 PAUSED"
        await query.edit_message_text(
            f"📊 **Account Status**\n\n"
            f"• Trading: {status}\n"
            f"• Demo Balance: 100 ETH\n"
            f"• Profit Today: +{random.randint(1, 25)} ETH\n"
            f"• Total Trades: {random.randint(50, 200)}\n\n"
            f"Use the buttons below to continue."
        )
    
    # Show main menu again
    keyboard = [
        [InlineKeyboardButton("💰 Deposit", callback_data='deposit')],
        [InlineKeyboardButton("📈 Trade", callback_data='trade')],
        [InlineKeyboardButton("⏯️ Stop/Start", callback_data='toggle_trade')],
        [InlineKeyboardButton("💸 Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("📊 Status", callback_data='status')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Choose an option:", reply_markup=reply_markup)

# Handle address input for withdrawal
async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_address'):
        eth_address = update.message.text
        
        # Simple validation for ETH address (basic check)
        if eth_address.startswith('0x') and len(eth_address) == 42:
            await update.message.reply_text(
                f"🎉 **Congratulations!**\n\n"
                f"✅ 10 ETH profit is coming your way!\n\n"
                f"Transaction sent to:\n`{eth_address}`\n\n"
                f"Estimated arrival: 2-5 minutes\n"
                f"Transaction ID: `0x{''.join(random.choices('0123456789abcdef', k=64))}`",
                parse_mode='Markdown'
            )
            context.user_data['awaiting_address'] = False
        else:
            await update.message.reply_text(
                "⚠️ Please enter a valid ETH address (should start with 0x and be 42 characters long).\n\n"
                "Try again:"
            )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f'Update {update} caused error {context.error}')

# Main function
def main():
    # Create Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # Run Flask app in a separate thread for Render
    from threading import Thread
    Thread(target=lambda: app.run(host='0.0.0.0', port=PORT, debug=False)).start()
    
    # Start the bot
    main()
