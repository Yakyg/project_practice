# Структра [/src](https://github.com/Yakyg/project_practice/tree/main/src)
```markdawn
/ src
├── Dockerfile          # Cборка Docker-контейнера
├── bot.py              # Исполнительный файл
├── data.json           # Хранилище данных
└── requirements.txt    # Список зависимостей
```

# Описание
- Телеграм-бот SafetyBot ([@Safety_aid_bot](https://t.me/Safety_aid_bot)) - это бот-помощник по безопасности, предоставляющий информацию о оказании первой помощи, ежедненво напоминает о правилах безопасности и дает возможность пройти викторину по правилам безопасности.
- Как работает
  - Пользователь выбирает функцию (викторина или оказание первой помощи), а бот предоставляет в соответствии с выбором проводит викторину, либо дает выбрать направление оказания первой помощи(например ПП при ожоге). после чего бот дает иструкцию.
- Преимущества
  - Легкий доступ к информации
  - Dозможность быстро получить нужную инструкцию в экстренной ситуации

# Функционал
- Кнопки:
    - Викторина - Сыграть в викторину о правилах безопасноти.
    - Советы по первой помощи - Получить информацию о необходимых действиях при оказании первой помощи.
    - Описание бота - Получить описание возможностей бота.
- Локальная база в формате JSON

# Планируемый функционал
- Расширение базы информации о оказании первой помощи
- Доработка викторины


# Изучение технологии
- Ресурсы:
  - [Официальная документация Telegram Bot API](https://core.telegram.org/)
  - [Гайд видео-курс "Телеграм бот на Python"](https://www.youtube.com/watch?v=ObwoMskHDoA)
  - [Гайд "Телеграм Бот на Python с нуля!"](https://www.youtube.com/watch?v=7mdyOUjECP0)
## Этап 1: Реализация минимального функционала
1) Получение токена бота с помощью официального тг-бота BotFather

![image](https://www.google.com/imgres?q=%D0%B1%D0%BE%D1%82%20%D1%84%D0%B0%D0%B7%D0%B5%D1%80&imgurl=https%3A%2F%2Fblog.ringostat.com%2Fwp-content%2Fuploads%2F2019%2F04%2Fbot-fazer.png&imgrefurl=https%3A%2F%2Fblog.ringostat.com%2Fru%2Fsozdaem-chat-bot-v-telegram%2F&docid=1fMG0COpwnMz-M&tbnid=7tPPprWj6g5_2M&vet=12ahUKEwiO0t6j3eaNAxWy3AIHHftIMkcQM3oECFAQAA..i&w=475&h=483&hcb=2&ved=2ahUKEwiO0t6j3eaNAxWy3AIHHftIMkcQM3oECFAQAA)

2) Реализация
  - Написание минимального бота с помощью официальной документации
```python
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот-помощник!.")

app = ApplicationBuilder().token("YOUR_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
```
## Этап 2: Разработка функционала
Основные компоненты:
1) Меню с инлайн-кнопками:
```python
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
```
2) Система отправки совета дня:
```python
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

```
## Этап 3: Работа с данными
- Структура данных (data.json):
```json
{
  "quiz": [
    {
      "question": "Что нужно сделать первым делом при обнаружении пострадавшего на рабочем месте?",
      "options": [
        "Оказать первую помощь и вызвать скорую",
        "Дождаться указаний начальства",
        "Не вмешиваться"
      ],
      "answer": 0
    },
      "daily_tips": [
    "Перед началом работы убедитесь в исправности оборудования.",
    "Работайте в спецодежде и используйте средства индивидуальной защиты.",
    "Соблюдайте порядок на рабочем месте — это снижает риск травм.",
    "При обнаружении опасной ситуации немедленно сообщите руководителю.",
    "Не работайте на высоте без страховочных средств.",
    "Перед началом работы внимательно изучите инструкции по безопасности для вашего участка.",
    "Не используйте неисправное оборудование — сообщайте о поломках ответственному лицу.",
    "мойте руки после работы с химическими веществами.",
    "При работе с электроинструментом используйте защитные очки и перчатки.",
    "Не оставляйте посторонние предметы на проходах — это может привести к травме.",
    "Храните легковоспламеняющиеся вещества в специально отведённых местах.",
    "Проверяйте наличие и исправность огнетушителей на рабочем месте.",
    "При первых признаках недомогания — прекратите работу и обратитесь за медицинской помощью.",
    "Работайте только в трезвом состоянии — алкоголь и наркотики категорически запрещены!",
    "Всегда знайте местоположение аптечки и ближайших аварийных выходов."

  ]
}

```
## Этап 4: Логирование
```python
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
```
## Этап 5: Развертывание
- Docker-контейнеризация
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data.json bot.py ./

ENV TELEGRAM_TOKEN=""

CMD ["python", "bot.py"]

```
- Сборка и запуск:
```bash
docker build -t o-bot .
docker run -d -e TELEGRAM_TOKEN --name o-bot o-bot
```
