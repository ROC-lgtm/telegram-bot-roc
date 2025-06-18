import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import logging
import time
import asyncio
import requests
from telebot.handler_backends import BaseMiddleware
from telebot import types

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("Початок виконання скрипта")

# Налаштування Telegram бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
KEEP_ALIVE_URL = os.getenv("RENDER_EXTERNAL_URL")  # Наприклад, https://your-service.onrender.com

# Перевірка змінних оточення
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не встановлено. Перевірте змінні оточення.")
    raise ValueError("BOT_TOKEN не встановлено")

try:
    bot = telebot.TeleBot(BOT_TOKEN)
    logger.info("Бот ініціалізовано")
except Exception as e:
    logger.error(f"Помилка ініціалізації бота: {e}")
    raise

# Middleware для обмеження частоти запитів
class RateLimitMiddleware(BaseMiddleware):
    def __init__(self):
        self.last_request = {}

    def pre_process(self, message, data):
        chat_id = message.chat.id if isinstance(message, types.Message) else message.from_user.id
        current_time = time.time()
        if chat_id in self.last_request:
            if current_time - self.last_request[chat_id] < 0.5:  # Обмеження: 0.5 сек
                return None  # Пропускаємо запит
        self.last_request[chat_id] = current_time
        return data

    def post_process(self, message, data, exception):
        pass

bot.setup_middleware(RateLimitMiddleware())

# Функція для "пінгування" сервера
def keep_alive():
    if KEEP_ALIVE_URL:
        try:
            response = requests.get(KEEP_ALIVE_URL)
            logger.info(f"Keep-alive ping: {response.status_code}")
        except Exception as e:
            logger.error(f"Помилка keep-alive: {e}")

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
    try:
        bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="Markdown")
        logger.info(f"Відправлено головне меню для chat_id: {chat_id}")
    except Exception as e:
        logger.error(f"Помилка відправки головного меню: {e}")

# Обробник /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    logger.info(f"Отримано команду /start від {message.chat.id}")
    send_main_menu(message.chat.id)

# Обробник callback-запитів
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    logger.info(f"Отримано callback: {call.data} від {chat_id}")

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
            markup = tpl_back()
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "fop2":
            text = (
                "👤 *ФОП 2 група (єдиний податок)*\n"
                "*Базовий тариф:* 400 грн/міс\n\n"
                "*Діяльність дозволена:*\n"
                "• Продаж товарів будь‑кому\n"
                "• Надання послуг населенню та платникам єдиного податку\n"
                "• До 10 найманих працівників\n\n"
                "*У тариф входить:*\n"
                "✅ Розрахунок доходу та Книги обліку\n"
                "✅ Контроль ліміту доходу\n"
                "✅ Нагадування про сплату, формування реквізитів, контроль оплат\n"
                "✅ Оплата податків бухгалтером (за доступом)\n"
                "✅ Щомісячний аудит кабінету\n"
                "✅ Подання звітності, заяв, листів, запитів\n"
                "✅ Підтримка під час супроводу\n\n"
                "📌 *Додатково:* при використанні РРО/еквайрингу — +200 грн/міс"
            )
            markup = tpl_back().add(InlineKeyboardButton("👥 Тариф із найманими працівниками", callback_data="fop_staff"))
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "fop3nopdv":
            text = (
                "👤 *ФОП 3 група (єдиний податок без ПДВ)*\n"
                "*Базовий тариф:* 400 грн/міс\n\n"
                "*Діяльність дозволена:*\n"
                "• Продаж і послуги будь‑кому\n"
                "• Необмежена кількість працівників\n\n"
                "*У тариф входить:*\n"
                "✅ Розрахунок доходу та Книги обліку\n"
                "✅ Контроль ліміту доходу\n"
                "✅ Нагадування, формування реквізитів, контроль оплат\n"
                "✅ Оплата податків бухгалтером (за доступом)\n"
                "✅ Щомісячний аудит кабінету\n"
                "✅ Подання звітності, заяв, листів, запитів\n"
                "✅ Підтримка супроводу\n\n"
                "📌 *Додатково:* при РРО/еквайрингу — +200 грн/міс"
            )
            markup = tpl_back().add(InlineKeyboardButton("👥 Тариф із найманими працівниками", callback_data="fop_staff"))
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "fop3pdv":
            text = (
                "👤 *ФОП 3 група (єдиний податок з ПДВ)*\n"
                "*Базовий тариф:* 3500 грн/міс\n\n"
                "*Діяльність дозволена:*\n"
                "• Продаж і послуги будь‑кому\n"
                "• Необмежена кількість працівників\n\n"
                "*У тариф входить:*\n"
                "✅ Розрахунок доходу та Книги обліку\n"
                "✅ Контроль ліміту доходу\n"
                "✅ Нагадування, формування реквізитів, контроль оплат\n"
                "✅ Оплата податків бухгалтером (за доступом)\n"
                "✅ Щомісячний аудит кабінету\n"
                "✅ Подання звітності, заяв, листів, запитів\n"
                "✅ Підтримка супроводу\n\n"
                "💰 *Блок ПДВ:*\n"
                "✅ Рахунки‑накладні, акти (до 10/міс)\n"
                "✅ Реєстрація в ЄРПН\n"
                "✅ Контроль вхідних накладних\n"
                "✅ Перевірка УКТ ЗЕД\n"
                "✅ Моніторинг ліміту в СЕА ПДВ\n"
                "✅ Подання декларації з ПДВ\n"
                "✅ Контроль сплати податку\n\n"
                "📌 *Вартість тарифу індивідуально — залежно від обсягу операцій та специфіки.*"
            )
            markup = tpl_back()
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "fop_staff":
            text = (
                "👤 *ФОП на єдиному податку (з найманими працівниками)*\n"
                "*Базовий тариф:* 2300 грн/міс\n\n"
                "*У тариф входить:*\n"
                "✅ Розрахунок доходу та Книги обліку\n"
                "✅ Контроль ліміту доходу\n"
                "✅ Нагадування, формування реквізитів, контроль оплат\n"
                "✅ Оплата податків бухгалтером (за доступом)\n"
                "✅ Щомісячний аудит кабінету\n"
                "✅ Подання звітності, заяв, листів, запитів\n"
                "✅ Підтримка супроводу\n\n"
                "👥 *Зарплатний блок:*\n"
                "✅ Нарахування зарплати (до 3 працівників)\n"
                "✅ Два рази на місяць виплати та податки\n"
                "✅ Платіжні відомості (клієнт‑банк)\n"
                "✅ Кадрові документи (накази)\n"
                "✅ Відпустки, лікарняні, індексація\n"
                "✅ Зарплатна звітність\n\n"
                "📌 Кожен наступний працівник +100 грн/міс"
            )
            markup = tpl_back()
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "fop_general":
            text = (
                "👤 *ФОП на загальній системі*\n"
                "*Базовий тариф:* 3500 грн/міс\n\n"
                "*У тариф входить:*\n"
                "✅ Розрахунок доходу та ведення Книги обліку доходів та витрат\n"
                "✅ Ведення Форми обліку товарних запасів\n"
                "✅ Контроль ліміту доходу 1 млн (для реєстрації платником ПДВ)\n"
                "✅ Нагадування про сплату податків, формування реквізитів, контроль оплат\n"
                "✅ Можливість здійснення оплат податків бухгалтером (за доступом)\n"
                "✅ Щомісячний аудит електронного кабінету\n"
                "✅ Подання податкової звітності, заяв, листів, запитів\n"
                "✅ Розрахунок акцизного податку, подання Декларації з акцизного податку\n"
                "✅ Відповіді на запитання в процесі супроводу\n\n"
                "📌 *Додатково:* наявність найманих працівників — +1500 грн/міс"
            )
            markup = tpl_back()
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "llc":
            text = (
                "🏢 *ТОВ/ПП*\n"
                "*Базовий тариф:* 5000 грн/міс\n\n"
                "*У тариф входить:*\n"
                "✅ Відображення операцій на рахунках бухгалтерського обліку\n"
                "✅ Подання фінансової та податкової звітності, заяв, листів, запитів\n"
                "✅ Контроль ліміту доходу 1 млн (для реєстрації платником ПДВ)\n"
                "✅ Нагадування про сплату податків, формування реквізитів, контроль оплат\n"
                "✅ Можливість здійснення оплат податків та контрагентам бухгалтером (за доступом)\n"
                "✅ Щомісячний аудит електронного кабінету\n"
                "✅ Нарахування та виплата заробітної плати\n"
                "✅ Базові кадрові документи (Накази)\n"
                "✅ Відповіді на запитання в процесі супроводу\n\n"
                "📌 *Вартість тарифу розраховується індивідуально — залежно від*\n"
                "• системи оподаткування (загальна/спрощена)\n"
                "• статусу платника ПДВ\n"
                "• виду діяльності\n"
                "• обсягу операцій, кількості документів і- специфіки вашої діяльності, придбаного програмного забезпечення (MeDoc)\n"
                "• кількості найманих працівників\n"
                "• випадків блокування податкових накладних"
            )
            markup = tpl_back()
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "reg_fop":
            text = (
                "📝 *Реєстрація ФОП*\n"
                "*Вартість:* 1000 грн\n\n"
                "*У вартість входить:*\n"
                "✅ Попередня консультація\n"
                "✅ Вибір оптимальної системи оподаткування\n"
                "✅ Підбір КВЕД під види діяльності\n"
                "✅ Допомога із створенням електронного підпису\n"
                "✅ Перевірка відсутності податкового боргу\n"
                "✅ Подання заяви на реєстрацію ФОП\n"
                "✅ Перевірка правильності поставлення ФОП на облік\n"
                "✅ Виписка про реєстрацію ФОП та Витяг платника єдиного податку\n"
                "✅ Подання Форми 20-ОПП\n"
                "✅ Реєстрація ПРРО\n"
                "✅ Допомога з відкриттям рахунку в банку\n"
                "✅ Надання реквізитів для оплати податків"
            )
            markup = tpl_back()
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "close_fop":
            text = (
                "📝 *Закриття ФОП*\n"
                "*Вартість:* 1500 грн\n\n"
                "*У вартість входить:*\n"
                "✅ Попередня консультація\n"
                "✅ Розрахунок доходу\n"
                "✅ Перевірка податкового кабінету\n"
                "✅ Допомога із створенням електронного підпису\n"
                "✅ Перевірка відсутності податкового боргу\n"
                "✅ Подання заяви на закриття ФОП\n"
                "✅ Виписка про закриття ФОП\n"
                "✅ Подання ліквідаційної податкової декларації\n"
                "✅ Подання Форми 20-ОПП на зняття об'єктів\n"
                "✅ Скасування реєстрації ПРРО"
            )
            markup = tpl_back()
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "decl_fop":
            text = (
                "📑 *Декларація ФОП на ЄП*\n"
                "*Вартість:* 1000 грн\n\n"
                "*У вартість входить:*\n"
                "✅ Розрахунок доходу\n"
                "✅ Перевірка податкового кабінету\n"
                "✅ Допомога із створенням електронного підпису\n"
                "✅ Перевірка відсутності податкового боргу\n"
                "✅ Подання податкової декларації"
            )
            markup = tpl_back()
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")

        elif call.data == "contacts":
            text = (
                "📞 Зв’яжіться з нами у зручний спосіб:\n\n"
                "📱 Телефон/Viber/Telegram: +38 (098) 159‑75‑70\n"
                "✉️ Email: r.o.c@ukr.net\n"
                "📲 [Instagram](https://www.instagram.com/reliable_outsorsing_company/)\n"
                "💬 [Telegram](https://t.me/Reliable_Outsorsing_Company)\n"
                "💬 [WhatsApp](https://wa.me/380981597570)"
            )
            markup = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🔙 Повернутися до головного меню", callback_data="main_menu")
            )
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)

        elif call.data == "about":
            text = (
                "👤 *Про компанію*\n\n"
                "*Reliable Outsorsing Company* – бухгалтерська аутсорсингова компанія, яка наслідує європейський сервіс обслуговування та ділові відносини. Для нас важливий кожен клієнт і тому прагнемо забезпечити якісний сервіс обслуговування та задовільнити Ваші потреби. А професіоналізм і відповідальне ставлення до поставлених завдань підтверджено більш ніж 10-річним досвідом роботи з різними організаційними формами, видами діяльності та системами оподаткування.\n\n"
                "*Надаємо професійні бухгалтерські послуги:*\n"
                "✅ Бухгалтерське обслуговування для ФОП та ТОВ\n"
                "✅ Консультація з питань вибору системи оподаткування при створенні підприємства\n"
                "✅ Відкриття ФОП, підбір групи єдиного податку та КВЕДів, відкриття банківського рахунку\n"
                "✅ Закриття ФОП, ліквідаційні звіти\n"
                "✅ Формування та подання звітності в контролюючі органи\n"
                "✅ Виготовлення ключів електронного цифрового підпису (ЕЦП/КЕП)\n"
                "✅ Налагодження системи бухгалтерського обліку\n"
                "✅ Нарахування заробітної плати, індексація, відпустки, лікарняні\n"
                "✅ Оформлення первинних документів\n"
                "✅ Консультація з питань необхідності використання РРО та ПРРО, реєстрація ПРРО\n"
                "✅ Контроль сплати всіх податків, формування реквізитів, платіжних документів, контроль вчасної сплати та актуальності рахунків\n"
                "✅ Консультація штатному бухгалтеру та допомога у вирішенні специфічних питань\n\n"
                "📞 *Телефонуйте або пишіть нам у будь-який зручний для Вас час, а ми запропонуємо і впровадимо оптимальні варіанти, що підходять саме для Вашого бізнесу:*\n"
                "📲 [Instagram](https://www.instagram.com/reliable_outsorsing_company/)\n"
                "💬 Viber/Telegram: 098-159-75-70\n"
                "✉️ e-Mail: r.o.c@ukr.net\n\n"
                "Делегуйте ведення бухгалтерського обліку нам, спрямуйте час і ресурси на дійсно важливі процеси функціонування і розширення Вашого бізнесу та будуймо Україну майбутнього разом."
            )
            markup = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🔙 Повернутися до головного меню", callback_data="main_menu")
            )
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=True)

        elif call.data == "main_menu":
            send_main_menu(chat_id)

        bot.answer_callback_query(call.id)  # Підтверджуємо callback

    except Exception as e:
        logger.error(f"Помилка обробки callback {call.data}: {e}")
        bot.answer_callback_query(call.id, "Виникла помилка. Спробуйте ще раз.")

# Асинхронна функція для polling із повторними спробами
async def run_polling():
    logger.info("Запуск polling...")
    while True:
        try:
            await bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            logger.error(f"Помилка polling: {e}")
            keep_alive()  # Пінгуємо сервер для підтримки активності
            await asyncio.sleep(10)  # Чекаємо 10 секунд перед перезапуском

# Запуск бота
if __name__ == "__main__":
    logger.info("Скрипт запущено")
    try:
        bot.remove_webhook()
        logger.info("Webhook видалено")
    except Exception as e:
        logger.error(f"Помилка видалення webhook: {e}")

    try:
        asyncio.run(run_polling())
    except Exception as e:
        logger.error(f"Критична помилка запуску: {e}")
        raise
