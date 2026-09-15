import os
import time
import requests
import asyncio
import nest_asyncio
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

nest_asyncio.apply()

# Render Web Service PORT binding
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

BOT_TOKEN = "8952937185:AAF0qjCMokwh43ag7PEor409ATwpoZowf0"
API_URL = "https://api-inference.huggingface.co/models/damo-vilab/text-to-video-ms-1.7b"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 স্বাগতম! আমাকে কোনো ইংরেজি প্রম্পট লিখে পাঠান, আমি AI ভিডিও বানিয়ে দেব।")

async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    status_msg = await update.message.reply_text("🎬 আপনার প্রম্পট থেকে AI ভিডিও তৈরি হচ্ছে... ১-২ মিনিট সময় দিন।")

    try:
        response = requests.post(API_URL, json={"inputs": prompt})
        
        if response.status_code == 503:
            await status_msg.edit_text("⏳ AI মডেল চালু হচ্ছে... ৩০ সেকেন্ড পর অটো রিট্রাই করা হচ্ছে।")
            time.sleep(30)
            response = requests.post(API_URL, json={"inputs": prompt})

        if response.status_code == 200:
            with open("generated_video.mp4", "wb") as f:
                f.write(response.content)
            
            await status_msg.edit_text("✅ ভিডিও তৈরি শেষ! পাঠাচ্ছি...")
            await update.message.reply_video(video=open("generated_video.mp4", "rb"), caption=f"Prompt: {prompt}")
            os.remove("generated_video.mp4")
        else:
            await status_msg.edit_text(f"❌ ভিডিও তৈরিতে সমস্যা হয়েছে। সার্ভার স্ট্যাটাস: {response.status_code}")

    except Exception as e:
        await status_msg.edit_text(f"❌ এরর: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_video))
    app.run_polling()

if __name__ == "__main__":
    main()
    
