import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import os
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ініціалізація Flask
app = Flask(__name__)

# Налаштування Telegram бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Наприклад, https://telegram-bot-roc.onrender.com/webhook

# Перевірка змінних оточення
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не встановлено. Перевірте змінні оточення.")
    raise ValueError("BOT_TOKEN не встановлено")
if not WEBHOOK_URL:
    logger.error("WEBHOOK_URL не встановлено. Перевірте змінні оточення.")
    raise ValueError("WEBHOOK_URL не встановлено")

bot = telebot.TeleBot(BOT_TOKEN)

# Видаляємо старий webhook
try:
    bot.remove_webhook()
    logger.info("Старий webhook видалено")
except Exception as e:
    logger.error(f"Помилка видалення старого webhook: {e}")

# Встановлюємо новий webhook
try:
    bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Webhook встановлено: {WEBHOOK_URL}")
except Exception as e:
    logger.error(f"Помилка встановлення webhook: {e}")
    raise

# Головна сторінка
@app.route('/')
def home():
    return "Telegram Bot is running!"

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return '', 200
        else:
            logger.warning("Невірний content-type у запиті")
            return '', 403
    except Exception as e:
        logger.error(f"Помилка обробки webhook: {e}")
        return '', 500

# Функція головного меню
def send_main_menu(chat_id):
    welcome_text = (
        "Вас вітає\n"
        "*Reliable Outsorsing Company* –\n"
        "бухгалтерська аутсорсингова компанія"
    )
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📋 Ціни", callback_data="prices"),
        InlineKeyboardButton("📲 Instagram", url="https://www.instagram.com/reliable_outsorsing_company/"),
        InlineKeyboardButton("💼 Контакти", callback_data="contacts"),
        InlineKeyboardButton("👤 Про компанію", callback_data="about")
    )
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# Обробник /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    send_main_menu(message.chat.id)

# Обробник callback-запитів
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    def tpl_back():
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("💼 Наші контакти", callback_data="contacts"),
            InlineKeyboardButton("🔙 Повернутися до попереднього меню", callback_data="prices")
        )

    try:
        if call.data == "prices":
            text = (
                "💼 *Тарифи на бухгалтерське обслуговування ФОП*\n"
                "🧾 Кожен тариф включає базові послуги: підготовку звітності, контроль платежів, консультації та перевірку електронного кабінету.\n"
                "👇 Оберіть потрібний тариф нижче:"
            )
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("1️⃣ ФОП 1 група — від 400 грн/міс", callback_data="fop1"),
                InlineKeyboardButton("2️⃣ ФОП 2 група — від 400 грн/міс", callback_data="fop2"),
                InlineKeyboardButton("3️⃣ ФОП 3 група (без ПДВ) — від 400 грн/міс", callback_data="fop3nopdv"),
                InlineKeyboardButton("3️⃣ ФОП 3 група (з ПДВ) — від 3500 грн/міс", callback_data="fop3pdv"),
                InlineKeyboardButton("🧍‍♂️ ФОП з працівниками — від 2300 грн/міс", callback_data="fop_staff"),
                InlineKeyboardButton("📑 ФОП на загальній системі — від 3500 грн/міс", callback_data="fop_general"),
                InlineKeyboardButton("🏢 ТОВ/ПП — від 5000 грн/міс", callback_data="llc"),
                InlineKeyboardButton("📝 Реєстрація ФОП — 1000 грн", callback_data="reg_fop"),
                InlineKeyboardButton("❌ Закриття ФОП — 1500 грн", callback_data="close_fop"),
                InlineKeyboardButton("📑 Декларація ФОП на ЄП — 1000 грн", callback_data="decl_fop"),
                InlineKeyboardButton("🔙 Повернутися до головного меню", callback_data="main_menu")
            )
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "fop1":
            text = (
                "👤 *ФОП 1 група (єдиний податок)*\n"
                "*Базовий тариф:* 400 грн/міс\n\n"
                "*Дозволена діяльність:*\n"
                "• Продаж товарів із торгових місць на ринках\n"
                "• Надання побутових послуг населенню\n"
                "• Можливість працювати без використання РРО\n"
                "• Без найманих працівників\n\n"
                "*У тариф входить:*\n"
                "✅ Розрахунок доходу та ведення Книги обліку\n"
                "✅ Контроль ліміту доходу відповідно до групи\n"
                "✅ Нагадування про сплату податків, формування реквізитів, контроль оплат\n"
                "✅ Можливість здійснення оплат податків бухгалтером (за доступом)\n"
                "✅ Щомісячний аудит електронного кабінету\n"
                "✅ Подання податкової звітності, заяв, листів, запитів\n"
                "✅ Відповіді на запитання в процесі супроводу\n\n"
                "📌 *Додатково:* при використанні РРО та/або еквайрингу — +100 грн/міс"
            )
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("💼 Наші контакти", callback_data="contacts"),
                InlineKeyboardButton("🔙 Повернутися до попереднього меню", callback_data="prices")
            )
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        # Додайте решту обробників (fop2, fop3nopdv, fop3pdv, fop_staff, fop_general, llc, reg_fop, close_fop, decl_fop, contacts, about, main_menu)
        elif call.data == "main_menu":
            send_main_menu(chat_id)

    except Exception as e:
        logger.error(f"Помилка обробки callback: {e}")
        bot.answer_callback_query(call.id, "Виникла помилка. Спробуйте ще раз.")

# Запуск сервера
if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))  # Використовуємо порт Render
    app.run(host='0.0.0.0', port=port)
