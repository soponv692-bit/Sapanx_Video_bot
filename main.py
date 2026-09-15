
import os, asyncio, nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from moviepy.editor import VideoFileClip, concatenate_videoclips

nest_asyncio.apply()

BOT_TOKEN = "8952937185:AAEydqFowh44l6GiSbU0j8iZ3XToWdEVW14"

def make_progress_bar(percent):
    done = int(percent / 10)
    return "█" * done + "░" * (10 - done)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "🎬 **Sapanx Video Engine Bot**-এ স্বাগতম!\n📥 যেকোনো ভিডিও ফাইল পাঠালে ৩ সেকেন্ডের সেগমেন্টে এডিট হবে।"
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⚡ **এডিটিং শুরু হচ্ছে...**", parse_mode="Markdown")
    
    try:
        video_file = await update.message.video.get_file()
        input_path = "user_input.mp4"
        await video_file.download_to_drive(input_path)
        
        clip = VideoFileClip(input_path)
        total_duration = int(clip.duration)
        chunk_duration = 3
        chunks = []
        
        for i in range(0, total_duration, chunk_duration):
            sub_clip = clip.subclip(i, min(i + chunk_duration, total_duration))
            chunk_filename = f"chunk_{i}.mp4"
            sub_clip.write_videofile(chunk_filename, codec="libx264", audio=False, verbose=False, logger=None)
            chunks.append(chunk_filename)
        
        clip.close()
        
        processed_clips = [VideoFileClip(c) for c in chunks]
        final_clip = concatenate_videoclips(processed_clips)
        
        output_path = "final_output.mp4"
        final_clip.write_videofile(output_path, codec="libx264", verbose=False, logger=None)
        
        for c in processed_clips:
            c.close()
        final_clip.close()
        
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=open(output_path, 'rb'),
            caption="✅ **ভিডিও প্রসেসিং সফল হয়েছে!**",
            parse_mode="Markdown"
        )
        
        os.remove(input_path)
        os.remove(output_path)
        for c in chunks:
            if os.path.exists(c):
                os.remove(c)
                
        await status_msg.delete()

    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text("❌ **ভিডিও প্রসেস করতে সমস্যা হয়েছে!**")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO, process_video))

if __name__ == "__main__":
    print("🤖 Sapanx Video Bot v2.0 রানিং আছে...")
    app.run_polling(drop_pending_updates=True)
