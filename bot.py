import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, VERSION
from database import DatabaseManager

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальный объект для работы с БД
db = DatabaseManager()

# Клавиатуры
def get_main_keyboard():
    """Создание главной клавиатуры бота"""
    keyboard = [
        [KeyboardButton("🛍️ Каталог")],
        [KeyboardButton("🔍 Поиск"), KeyboardButton("ℹ️ О нас")],
        [KeyboardButton("❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Обработчики команд
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"Пользователь {user.first_name} (ID: {user.id}) запустил бота")
    
    welcome_text = f"""
✨ Здравствуйте, {user.first_name}!

Добро пожаловать в Vogue Point - ваш онлайн-магазин модной одежды.

👕 Что я умею:
• Показывать каталог одежды по категориям
• Искать товары по размерам и цветам
• Давать полную информацию о товаре

💡 Используйте кнопки меню для навигации.

Версия бота: {VERSION}
"""
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📖 *Справка по использованию бота*

*Основные команды:*
/start - Начать работу с ботом
/catalog - Открыть каталог товаров
/help - Показать эту справку
/about - Информация о магазине

*Кнопки меню:*
🛍️ Каталог - Просмотр товаров по категориям
🔍 Поиск - Поиск по параметрам (в разработке)
ℹ️ О нас - Информация о магазине
❓ Помощь - Показать эту справку

*В ближайших обновлениях:*
- Фильтрация по размеру 👕
- Фильтрация по цвету 🎨
- Детальная информация о товаре 📊

По вопросам: support@voguepoint.ru
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /catalog - показывает категории"""
    logger.info("Запрос каталога товаров")
    
    # Подключаемся к БД
    if not db.connect():
        await update.message.reply_text("❌ Ошибка подключения к базе данных. Попробуйте позже.")
        return
    
    # Получаем категории
    categories = db.get_categories()
    db.disconnect()
    
    if not categories:
        await update.message.reply_text("📭 Каталог временно пуст. Загляните позже!")
        return
    
    # Формируем сообщение
    message = "🛍️ *Наш каталог:*\n\n"
    for cat_id, name, desc in categories:
        message += f"📌 *{name}*\n"
        message += f"   _{desc}_\n\n"
    
    message += "Скоро появится возможность просматривать товары по категориям!"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /about - информация о магазине"""
    about_text = """
👗 *Vogue Point* - современный магазин модной одежды

*О нас:*
📍 Основан в 2024 году
🌟 Более 500 довольных клиентов
🚚 Быстрая доставка по всей стране
💯 Гарантия качества

*Наши преимущества:*
• Только оригинальные бренды
• Примерка перед покупкой
• Возврат в течение 14 дней
• Сезонные скидки до 50%

*Контакты:*
📞 +7 (999) 123-45-67
📧 vogue@point.ru
📍 г. Москва, ул. Модная, 15

*Режим работы:* Пн-Вс с 10:00 до 21:00
"""
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных команд"""
    await update.message.reply_text(
        "❓ Неизвестная команда.\n"
        "Используйте /help для просмотра доступных команд."
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений (кнопок)"""
    text = update.message.text
    
    if text == "🛍️ Каталог":
        await catalog_command(update, context)
    elif text == "❓ Помощь":
        await help_command(update, context)
    elif text == "ℹ️ О нас":
        await about_command(update, context)
    elif text == "🔍 Поиск":
        await update.message.reply_text(
            "🔍 *Функция поиска в разработке*\n\n"
            "Скоро вы сможете искать товары по:\n"
            "• Размеру 👕\n"
            "• Цвету 🎨\n"
            "• Цене 💰\n\n"
            "Следите за обновлениями!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Используйте кнопки меню для навигации.\n"
            "Команда /help покажет все возможности."
        )

def main():
    """Запуск бота"""
    print("\n" + "="*50)
    print(f"ЗАПУСК БОТА VOGUE POINT v{VERSION}")
    print("="*50)
    
    # Проверяем наличие токена
    if BOT_TOKEN == "ВАШ_ТОКЕН_БУДЕТ_ЗДЕСЬ":
        print("\n⚠️ ВНИМАНИЕ: Токен бота не настроен!")
        print("1. Перейдите в Telegram к @BotFather")
        print("2. Создайте бота командой /newbot")
        print("3. Скопируйте токен в файл config.py")
        print("\nБот не может запуститься без токена!\n")
        return
    
    # Инициализация базы данных
    print("\nИнициализация базы данных...")
    if db.connect():
        db.create_tables()
        db.add_sample_data()
        db.disconnect()
        print("✓ База данных готова")
    else:
        print("✗ Ошибка инициализации БД")
        return
    
    # Создание приложения
    print("\nСоздание приложения бота...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("catalog", catalog_command))
    app.add_handler(CommandHandler("about", about_command))
    
    # Регистрация обработчика текстовых сообщений (кнопки)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
    
    # Регистрация обработчика неизвестных команд
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    print("✓ Обработчики зарегистрированы")
    print("\n" + "="*50)
    print("🚀 БОТ УСПЕШНО ЗАПУЩЕН!")
    print("="*50)
    print("\nПерейдите в Telegram и отправьте боту команду /start\n")
    
    # Запуск бота
    app.run_polling()

if __name__ == '__main__':
    main()