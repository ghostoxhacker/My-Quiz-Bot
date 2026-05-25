import logging, random, json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(level=logging.INFO)

# Config
UPDATE_CHNL = "https://t.me/Soothing_Sanctuary"
SUPPORT_GRP = "https://t.me/PrepNationGrp"
DEV_LINK = "https://t.me/Umm_hotty"
BOT_TOKEN = "8723527354:AAE7rzS-2_Vay87tF94FDDWczt6mENlb9_s"
BOT_USERNAME = "QuizariumProBot"

# Load Questions
with open('questions.json', 'r') as f:
    quiz_data = json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    context.user_data['lang'] = 'en'  # Default language
    
    links_kb = [
        [InlineKeyboardButton("📢 Updates", url=UPDATE_CHNL), InlineKeyboardButton("💬 Support", url=SUPPORT_GRP)],
        [InlineKeyboardButton("⚡ Developer", url=DEV_LINK)]
    ]
    
    welcome_text = (
        "What can this bot do?\n\n"
        "I'm Quizarium bot and I play Quizarium, a fast paced and addictive trivia-like game. "
        "Just add me to a group chat and start brainstorming with friends!\n\n"
        "Talk with me in private chat for help and guidance (hit Start)!"
    )
    
    if chat.type == 'private':
        kb = [[KeyboardButton("📊 Rankings"), KeyboardButton("🇺🇸/🇮🇳 Language")], [KeyboardButton("❓ Help")]]
        reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        await update.message.reply_text("Official Links:", reply_markup=InlineKeyboardMarkup(links_kb))
    else:
        start_kb = [[InlineKeyboardButton("🎮 Start Quiz", callback_data="game")]]
        await update.message.reply_text(
            "Quizarium game is ready! Click the button to start brainstorming with friends.", 
            reply_markup=InlineKeyboardMarkup(start_kb + links_kb)
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "lang_en":
        context.user_data['lang'] = 'en'
        await query.edit_message_text("Language set to English.")
    elif query.data == "lang_hi":
        context.user_data['lang'] = 'hi'
        await query.edit_message_text("Language set to Hindi.")
    
    elif query.data == "game":
        lang = context.user_data.get('lang', 'en')
        filtered_q = [q for q in quiz_data if q['lang'] == lang]
        if not filtered_q:
            await query.edit_message_text("No questions available!")
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
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
  
