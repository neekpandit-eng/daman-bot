import sqlite3
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def init_db():
    conn = sqlite3.connect('daman_game.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_4_digit TEXT,
            result TEXT
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM results')
    count = cursor.fetchone()[0]
    if count == 0:
        import random
        sample_data = []
        outcomes = ['Small', 'Big']
        for i in range(1000):
            rand_4 = f"{random.randint(0, 9999):04d}"
            res = random.choice(outcomes)
            sample_data.append((rand_4, res))
        cursor.executemany("INSERT INTO results (last_4_digit, result) VALUES (?, ?)", sample_data)
        conn.commit()
    conn.close()

def check_trend_4_digit(last_4_input):
    conn = sqlite3.connect('daman_game.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT result, COUNT(*) FROM results 
        WHERE last_4_digit = ? 
        GROUP BY result
    ''', (last_4_input,))
    data = cursor.fetchall()
    
    if not data:
        cursor.execute('SELECT result, COUNT(*) FROM results GROUP BY result')
        data = cursor.fetchall()
    conn.close()
    
    results_count = {row[0]: row[1] for row in data}
    small_count = results_count.get('Small', 5)
    big_count = results_count.get('Big', 5)
    
    if big_count >= small_count:
        return "Big"
    else:
        return "Small"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 Enter 4 Digits & Submit", callback_data="input_prompt")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎮 **Daman Game Trend Analyser**\n\nNeeche diye gaye button par click karein:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "input_prompt":
        await query.message.reply_text(
            "✍️ Kripya game ka **last 4 digits** type karke bhejein (jaise: `0699`):"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    if user_text.isdigit() and len(user_text) == 4:
        sent_msg = await update.message.reply_text("🔄 hacking is going on...")
        await asyncio.sleep(1.5)
        
        await sent_msg.edit_text("✅ hacking is ✅")
        await asyncio.sleep(1)
        
        winning_result = check_trend_4_digit(user_text)
        await sent_msg.edit_text(f"📊 **Result:** {winning_result}")
    else:
        await update.message.reply_text("⚠️ Kripya sirf theek **4 digits** enter karein.")

if __name__ == '__main__':
    init_db()
    
    TOKEN = "8738157396:AAGyCwikL_2IaQ3mjSZ7z4RjQ9dyDGcpcFw"
    
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(30)
        .connect_timeout(30)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🤖 Daman Bot button menu ke sath live ho gaya hai...")
    app.run_polling()
