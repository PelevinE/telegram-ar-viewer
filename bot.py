from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import os

# Настроим параметры
TOKEN = "8297668613:AAG5nWJuOw5AIwy8d6rNXQ7SyXbSqKmV5BI"
WEBAPP_URL = "https://ТВОЙ_ДОМЕН/webapp-ar"  # поменяй на адрес своего webapp

# Папка для хранения файлов
if not os.path.exists("models"):
    os.makedirs("models")

# Команда старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне 3D модель в формате .glb или .gltf (до 50MB).\n"
        "Я сгенерирую ссылку для просмотра её в AR через WebApp.\n"
        "По желанию, напиши после файла описание или название."
    )

# Обработка входящих документов
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if not file.file_name.endswith(('.glb', '.gltf')):
        await update.message.reply_text("Только .glb или .gltf!")
        return

    # Скачиваем файл
    file_id = file.file_id
    user_id = update.message.from_user.id
    file_path = f"models/{user_id}_{file.file_name}"
    new_file = await context.bot.get_file(file_id)
    await new_file.download_to_drive(file_path)

    # Запрашиваем описание
    context.user_data['last_file_path'] = file_path
    context.user_data['last_file_name'] = file.file_name
    await update.message.reply_text(
        "Файл получен!\nНапиши, пожалуйста, короткое описание или название для модели (или просто отправь '-')"
    )

# Получаем описание после файла
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'last_file_path' not in context.user_data:
        await update.message.reply_text("Пожалуйста, сначала пришли файл .glb/.gltf")
        return
    desc = update.message.text if update.message.text != '-' else ''
    file_path = context.user_data['last_file_path']
    file_name = context.user_data['last_file_name']
    user_id = update.message.from_user.id

    # Теперь нам нужно сформировать ссылку. Для локального теста используем ссылку на свой сервер,
    # либо загрузи файл в облако (например, на Google Drive и получи публичную ссылку).
    # Здесь пример для локального файла (localhost):
    public_url = f"http://ТВОЙ_ДОМЕН/models/{user_id}_{file_name}"

    # Формируем ссылку на webapp
    import urllib.parse
    webapp_link = (
        f"{WEBAPP_URL}?"
        f"url={urllib.parse.quote_plus(public_url)}"
        f"&title={urllib.parse.quote_plus(file_name)}"
        f"&desc={urllib.parse.quote_plus(desc)}"
    )

    await update.message.reply_text(
        f"Вот ваша ссылка для просмотра модели в AR/3D:\n{webapp_link}"
    )

    # Очищаем временные данные
    context.user_data.clear()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен!")
    app.run_polling()
