import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# --- FLASK WEB SERVER ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "YouTube Premium Bot is running live!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)

# --- BOT CONFIGURATION ---
BOT_TOKEN = "8241739750:AAHjOku2h5pYwfhGoFYRoVoLwOx5dhF8cDg"
ADMIN_ID = 8313247547
UPI_ID = "7276052050@fam"
AMOUNT = 60
FILE_LINK = "https://t.me/+CaIVPXNHg91jMWQ9"

QR_CODE_URL = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=Merchant%26am={AMOUNT}%26cu=INR"

WAITING_FOR_SCREENSHOT = 1
WAITING_FOR_UTR = 2

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = (
        f"Aapka swagat hai, {user.first_name}!\n\n"
        f"YouTube Premium (Lifetime With Updates) Lene ke liye aapko **₹{AMOUNT}** ka payment karna hoga.\n"
        f"📌 **UPI ID:** `{UPI_ID}`\n\n"
        f"Upar diye gaye QR Code ko scan karke payment karein. **Kripya exact ₹{AMOUNT} hi bhejein.**\n\n"
        f"Payment karne ke baad, Payment ka **Screenshot** yahan bhejein.\n\n"
        f"👑 Owner - Aditya Services (@asoffcial) 👑"
    )
    
    await update.message.reply_photo(
        photo=QR_CODE_URL,
        caption=msg,
        parse_mode="Markdown"
    )
    return WAITING_FOR_SCREENSHOT

async def receive_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file_id = update.message.photo[-1].file_id
    context.user_data["photo_id"] = photo_file_id
    
    await update.message.reply_text(
        "Screenshot mil gaya hai! Ab kripya apna **12-digit UTR / Transaction No** yahan type karke bhejein:"
    )
    return WAITING_FOR_UTR

async def receive_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utr_text = update.message.text
    user = update.effective_user

    await update.message.reply_text(
        "Wait Until Your Payment Is Verified , You Will Receive Your File Whithin 1 Hour"
    )

    admin_caption = (
        f"▶️ **Naya YouTube Premium Payment Request!**\n\n"
        f"👤 **User:** {user.first_name} (@{user.username})\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"💳 **Amount:** ₹{AMOUNT}\n"
        f"🔢 **UTR Number:** `{utr_text}`\n\n"
        f"⚙️ **Action Commands (Click to Copy):**\n"
        f"✅ **Approve:** `/approve {user.id}`\n"
        f"❌ **Reject:** `/reject {user.id}`"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=context.user_data["photo_id"],
        caption=admin_caption,
        parse_mode="Markdown"
    )

    return ConversationHandler.END

async def approve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: `/approve <user_id>`", parse_mode="Markdown")
        return

    try:
        target_user_id = int(context.args[0])
        
        # User ko link bhejna
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"✅ Aapka payment successfully approve ho gaya hai!\n\n📁 **Aapki YouTube Premium File / Channel Link:** {FILE_LINK}"
        )
        
        # Admin ko confirmation message
        await update.message.reply_text(
            f"✅ **Successful!** User `{target_user_id}` ko YouTube Premium link bhej diya gaya hai.",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: User ko message nahi bhej paye ({e})")

async def reject_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: `/reject <user_id>`", parse_mode="Markdown")
        return

    try:
        target_user_id = int(context.args[0])
        
        # User ko reject message bhejna
        await context.bot.send_message(
            chat_id=target_user_id,
            text="❌ Aapka payment reject kar diya gaya hai. Kripya sahi UTR aur Screenshot ke sath dobara koshish karein."
        )
        
        # Admin ko confirmation message
        await update.message.reply_text(
            f"❌ User `{target_user_id}` ka request reject kar diya gaya hai.",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: ({e})")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Process cancel ho gaya hai.")
    return ConversationHandler.END

def main():
    threading.Thread(target=run_flask, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FOR_SCREENSHOT: [MessageHandler(filters.PHOTO, receive_screenshot)],
            WAITING_FOR_UTR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_utr)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("approve", approve_cmd))
    app.add_handler(CommandHandler("reject", reject_cmd))

    print("YouTube Premium Bot running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
