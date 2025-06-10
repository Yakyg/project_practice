import os
import json
import logging
import random
from pytz import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from apscheduler.schedulers.background import BackgroundScheduler



def get_main_menu_markup():
    keyboard = [
        [InlineKeyboardButton("Описание бота", callback_data="about")],
        [InlineKeyboardButton("Викторина", callback_data="quiz")],
        [InlineKeyboardButton("Советы по первой помощи", callback_data="first_aid")],
    ]
    return InlineKeyboardMarkup(keyboard)


# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Загрузка данных
with open("data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

USERS_FILE = "users.json"
USERS = set()

def load_users():
    global USERS
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            USERS = set(json.load(f))

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(list(USERS), f)

# ===== Хэндлеры меню =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USERS.add(user_id)
    save_users()
    keyboard = [
        [InlineKeyboardButton("Описание бота", callback_data="about")],
        [InlineKeyboardButton("Викторина", callback_data="quiz")],
        [InlineKeyboardButton("Советы по первой помощи", callback_data="first_aid")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Выберите функцию:", reply_markup=reply_markup
    )

async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Этот бот поможет вам:\n"
        "• Проверить свои знания по охране труда в викторине\n"
        "• Получить советы по первой помощи при типовых травмах\n"
        "• Каждый день в 12:00 получать полезный совет по безопасности труда\n\n"
        "Чтобы начать, используйте /start."
    )


    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=get_main_menu_markup())
    else:
        await update.message.reply_text(text, reply_markup=get_main_menu_markup())

# ===== Викторина =====

QUIZ, QUIZ_ANSWER = range(2)

async def quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["quiz_questions"] = random.sample(DATA["quiz"], len(DATA["quiz"]))
    context.user_data["quiz_current"] = 0
    context.user_data["quiz_score"] = 0
    await send_quiz_question(update, context)
    return QUIZ

async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data["quiz_current"]
    questions = context.user_data["quiz_questions"]
    q = questions[idx]
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"quiz_answer:{i}")]
        for i, opt in enumerate(q["options"])
    ]
    if update.callback_query:
        await update.callback_query.edit_message_text(
            f"Вопрос {idx+1}/{len(questions)}:\n{q['question']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            f"Вопрос {idx+1}/{len(questions)}:\n{q['question']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = context.user_data["quiz_current"]
    questions = context.user_data["quiz_questions"]
    q = questions[idx]
    choice = int(query.data.split(":")[1])
    correct = q["answer"]
    if choice == correct:
        context.user_data["quiz_score"] += 1
        reply = "✅ Верно!"
    else:
        reply = f"❌ Неверно. Правильный ответ: {q['options'][correct]}"

    context.user_data["quiz_current"] += 1

    # Кнопки для продолжения или выхода в меню
    keyboard = []
    if context.user_data["quiz_current"] < len(questions):
        keyboard.append([InlineKeyboardButton("Следующий вопрос", callback_data="quiz_next")])
        keyboard.append([InlineKeyboardButton("Выйти в меню", callback_data="main_menu")])
    else:
        return await quiz_end(update, context)

    await query.edit_message_text(reply, reply_markup=InlineKeyboardMarkup(keyboard))
    return QUIZ


async def quiz_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_quiz_question(update, context)
    return QUIZ


async def quiz_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Выберите функцию:", reply_markup=get_main_menu_markup())
    context.user_data.clear()
    return ConversationHandler.END


async def quiz_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = context.user_data.get("quiz_score", 0)
    total = len(context.user_data.get("quiz_questions", []))
    await update.callback_query.edit_message_text(
        f"Викторина завершена!\nРезультат: {score} из {total} верно.",
        reply_markup=get_main_menu_markup()
    )
    context.user_data.clear()
    return ConversationHandler.END

# ===== Первая помощь =====

async def first_aid_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(k.title(), callback_data=f"aid:{k}")]
        for k in DATA["first_aid"].keys()
    ]
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "Выберите тип травмы:", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "Выберите тип травмы:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def first_aid_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, key = query.data.split(":", 1)
    steps = DATA["first_aid"][key]
    text = f"Первая помощь при «{key}»:\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
    await query.edit_message_text(text)
    await query.message.reply_text(
        "Что хотите сделать дальше?",
        reply_markup=get_main_menu_markup()
    )


# ===== Совет дня =====

async def send_daily_tip(app):
    tip = random.choice(DATA["daily_tips"])
    for user_id in USERS:
        try:
            await app.bot.send_message(user_id, f"💡 Совет дня:\n{tip}")
            
            await app.bot.send_message(
                user_id,
                "Что хотите сделать дальше?",
                reply_markup=get_main_menu_markup()
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить сообщение {user_id}: {e}")

def setup_daily_tip(app):
    scheduler = BackgroundScheduler(timezone=timezone("Europe/Moscow"))
    scheduler.add_job(lambda: app.create_task(send_daily_tip(app)), 'cron', hour=13, minute=0)
    scheduler.start()

# ====== Роутинг ======

def main():
    load_users()
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("Не задан TELEGRAM_TOKEN")
        return

    app = ApplicationBuilder().token(token).build()

    # Основное меню
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about_handler))
    # Инлайн-меню
    app.add_handler(CallbackQueryHandler(about_handler, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(first_aid_menu, pattern="^first_aid$"))
    app.add_handler(CallbackQueryHandler(first_aid_choice, pattern="^aid:"))
    # Викторина
    quiz_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(quiz_start, pattern="^quiz$"),
    ],
    states={
        QUIZ: [
            CallbackQueryHandler(quiz_answer, pattern="^quiz_answer:\\d+$"),
            CallbackQueryHandler(quiz_next, pattern="^quiz_next$"),
            CallbackQueryHandler(quiz_to_menu, pattern="^main_menu$"),
        ]
    },
    fallbacks=[CommandHandler("cancel", quiz_to_menu)],
)

    app.add_handler(quiz_conv)

    # Кнопка для меню первой помощи, если пользователь в диалоге
    app.add_handler(CommandHandler("first_aid", first_aid_menu))

    # Совет дня
    setup_daily_tip(app)
    
    
    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
