import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 অভিনন্দন! আপনি সফলভাবে বটটি চালু করেছেন।\n\n"
        "🔰 বটটি তৈরি করেছেন: @MsSumaiyaKhanom\n\n"
        "✏️ এখন আপনি একসাথে একাধিক মোবাইল নাম্বার পাঠাতে পারেন।"
    )

# When user sends numbers
async def handle_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Add 🔗 Link", callback_data='add_link'),
            InlineKeyboardButton("Add ➕", callback_data='add_plus'),
        ],
        [
            InlineKeyboardButton("Filter Prefix", callback_data='filter_prefix'),
        ],
        [
            InlineKeyboardButton("✅ JOIN OUR CHANNEL", url="https://t.me/HACKERA17X"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data["numbers"] = update.message.text
    await update.message.reply_text(
        "🛠️ Choose an action to perform on the numbers:\n\n🔧 Options below:",
        reply_markup=reply_markup
    )

# When a button is clicked
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    numbers_text = context.user_data.get("numbers", "")
    numbers = [line.strip() for line in numbers_text.splitlines() if line.strip()]

    action = query.data
    if action == 'add_link':
        result = "\n".join([f"t.me/+{n.lstrip('+')}" for n in numbers])
    elif action == 'add_plus':
        result = "\n".join([f"+{n.lstrip('+')}" for n in numbers])
    elif action == 'filter_prefix':
        result = "\n".join([n.lstrip('+').replace("t.me/", "").replace("https://", "") for n in numbers])
    else:
        result = "❌ Unknown action!"

    await query.message.reply_text(result)

# Main function to run bot
def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if name == 'main':
    main(https://t.me/HACKERA17X)
