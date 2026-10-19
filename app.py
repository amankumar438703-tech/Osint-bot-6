import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ==========================================
# YAHAN APNA TOKEN DAALEIN
BOT_TOKEN = "8951302382:AAF2dQn6fTlkAMq7Zr-67RAEV5I0Iyw5k1g"
# YAHAN APNI NUMVERIFY API KEY DAALEIN (https://numverify.com se free milegi)
NUMVERIFY_API_KEY = "1c75c1a50e1f04d9c78cbbd391a1e406"
# ==========================================

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- UI: Inline Keyboard Banane Ke Liye Helper ---
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📱 Number Info Kaise Lein?", callback_data='help_info')],
        [InlineKeyboardButton("🌐 API Key Kaise Lein?", callback_data='api_help')]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- /start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"👋 Namaste *{user_name}*!\n\n"
        "Main ek *Number Info Bot* hoon. Aap mujhe koi bhi mobile number bhejiye, "
        "main uski puri detail nikal kar dunga.\n\n"
        "📌 *Kaise Use Karein?*\n"
        "Bas number type karke send karein (Country code ke saath, jaise: `+919876543210`)\n\n"
        "Neeche diye gaye buttons se aur jaankari le sakte hain."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=get_main_menu())

# --- Button Click Handler ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'help_info':
        text = "📖 *Instructions:*\n1. Number copy karein.\n2. Chat box mein paste karke send karein.\n3. Agar number valid hua toh main detail bhej dunga."
    elif query.data == 'api_help':
        text = "🔑 *API Key:*\nYeh bot Numverify API use karta hai. Free key ke liye [yahan click karein](https://numverify.com)."
    else:
        text = "Kuch galat ho gaya."
        
    await query.edit_message_text(text, parse_mode='Markdown', disable_web_page_preview=True)

# --- Number Process Karne Wala Main Function ---
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    
    # Basic validation
    if len(number) < 5:
        await update.message.reply_text("❌ Yeh valid number nahi lag raha. Kripya country code ke saath number bhejein.")
        return

    processing_msg = await update.message.reply_text("🔍 *Number check ho raha hai...*", parse_mode='Markdown')

    # API Call
    api_url = "http://apilayer.net/api/validate"
    params = {
        'access_key': NUMVERIFY_API_KEY,
        'number': number,
        'format': 1
    }

    try:
        response = requests.get(api_url, params=params, timeout=10)
        data = response.json()

        if data.get('valid'):
            # Formatted Result (UI Design)
            result_text = (
                f"✅ *Number Info Found!*\n\n"
                f"📞 *Number:* `{data.get('international_format', 'N/A')}`\n"
                f"🌍 *Country:* {data.get('country_name', 'N/A')} ({data.get('country_code', 'N/A')})\n"
                f"📍 *Location:* {data.get('location', 'N/A')}\n"
                f"📡 *Carrier:* {data.get('carrier', 'N/A')}\n"
                f"📱 *Line Type:* {data.get('line_type', 'N/A')}\n\n"
                f"🤖 *Powered by Numverify*"
            )
        else:
            result_text = "❌ *Invalid Number!*\nKripya sahi format mein number bhejein (jaise: +919876543210)."

    except Exception as e:
        result_text = f"⚠️ *Error:* API se connect nahi ho paya. Thodi der baad try karein.\n`{str(e)}`"

    # Edit the processing message with result
    await processing_msg.edit_text(result_text, parse_mode='Markdown')

# --- Main Runner ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    print("🤖 Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()