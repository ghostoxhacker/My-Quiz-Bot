import logging
import random
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(level=logging.INFO)

# Config - Render ke Environment Variable se token uthayega
BOT_TOKEN = os.environ.get("BOT_TOKEN")
UPDATE_CHNL = "https://t.me/Soothing_Sanctuary"
SUPPORT_GRP = "https://t.me/PrepNationGrp"
DEV_LINK = "https://t.me/Umm_hotty"
BOT_USERNAME = "QuizariumProBot"

# Load Questions
try:
    with open('questions.json', 'r') as f:
        quiz_data = json.load(f)
except FileNotFoundError:
    quiz_data = []
    logging.error("questions.json file not found!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    context.user_data['lang'] = 'en'
    
    links_kb = [
        [InlineKeyboardButton("📢 Updates", url=UPDATE_CHNL), InlineKeyboardButton("💬 Support", url=SUPPORT_GRP)],
        [InlineKeyboardButton("⚡ Developer", url=DEV_LINK)]
    ]
    
    welcome_text = (
        "What can this bot do?\n\n"
        "I'm Quizarium bot and I play Quizarium, a fast paced and addictive trivia-like game. "
        "Just add me to a group chat and start brainstorming with friends!\n\n"
        "Talk with me in private chat for help and guidance!"
    )
    
    if chat.type == 'private':
        kb = [[KeyboardButton("📊 Rankings"), KeyboardButton("🇺🇸/🇮🇳 Language")], [KeyboardButton("❓ Help")]]
        reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        await update.message.reply_text("Official Links:", reply_markup=InlineKeyboardMarkup(links_kb))
    else:
        start_kb = [[InlineKeyboardButton("🎮 Start Quiz", callback_data="game")]]
        await update.message.reply_text(
            "Quizarium game is ready! Click the button to start brainstorming.", 
            reply_markup=InlineKeyboardMarkup(start_kb + links_kb)
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("lang_"):
        lang = query.data.split("_")[1]
        context.user_data['lang'] = lang
        await query.edit_message_text(f"Language set to {'English' if lang == 'en' else 'Hindi'}.")
        
    elif query.data == "game":
        lang = context.user_data.get('lang', 'en')
        filtered_q = [q for q in quiz_data if q.get('lang') == lang]
        
        if not filtered_q:
            await query.edit_message_text("No questions available for this language!")
            return
        
        q = random.choice(filtered_q)
        context.user_data['ans'] = q['a']
        await query.edit_message_text(f"Question: {q['q']}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🇺🇸/🇮🇳 Language":
        lang_kb = [[InlineKeyboardButton("English", callback_data="lang_en"), InlineKeyboardButton("Hindi", callback_data="lang_hi")]]
        await update.message.reply_text("Select language:", reply_markup=InlineKeyboardMarkup(lang_kb))
    elif text == "📊 Rankings":
        await update.message.reply_text("Top Players:\n1. Admin - 100 pts")
    elif text == "❓ Help":
        await update.message.reply_text("Add this bot to a group to play trivia games!")
    else:
        correct = context.user_data.get('ans')
        if correct and text.lower() == correct.lower():
            await update.message.reply_text("Correct! Well done.")
            context.user_data['ans'] = None

if __name__ == "__main__":
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN is missing! Set it in Render Environment Variables.")
    else:
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.run_polling()
        
