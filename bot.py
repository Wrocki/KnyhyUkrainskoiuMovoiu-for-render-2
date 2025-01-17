import aiohttp
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7554224281:AAFR9eSa7oxRilNmM2kuh3tIhDWJu1B08ws"
GROUP_ID = -1002411083990
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

async def search_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пошук книг через Telegram API"""
    if not context.args:
        await update.message.reply_text(
            "ℹ️ Як використовувати пошук:\n"
            "/search назва_книги\n"
            "Наприклад: /search Кобзар"
        )
        return

    query = " ".join(context.args).lower()
    status_message = await update.message.reply_text("🔍 Шукаю книгу...")

    try:
        async with aiohttp.ClientSession() as session:
            # Отримання останніх повідомлень
            url = f"{BASE_URL}getUpdates"
            async with session.get(url) as response:
                data = await response.json()

            if not data.get("ok"):
                raise Exception(f"Telegram API Error: {data}")

            found_books = []
            for result in data.get("result", []):
                message = result.get("message", {})
                if "document" in message:
                    file_name = message["document"]["file_name"].lower()
                    if query in file_name:
                        found_books.append(message)

                        if len(found_books) >= 5:  # Обмеження результатів
                            break

            if found_books:
                await status_message.edit_text(f"📚 Знайдено {len(found_books)} книг:")
                for book in found_books:
                    await context.bot.forward_message(
                        chat_id=update.effective_chat.id,
                        from_chat_id=GROUP_ID,
                        message_id=book["message_id"],
                    )
                logger.info(f"Знайдено {len(found_books)} книг для запиту: {query}")
            else:
                await status_message.edit_text("❌ Книгу не знайдено.")
                logger.info(f"Книгу не знайдено для запиту: {query}")

    except Exception as e:
        logger.error(f"Помилка пошуку: {str(e)}")
        await status_message.edit_text("⚠️ Помилка при пошуку. Спробуйте пізніше.")

def main():
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("search", search_book))
    application.run_polling()

if __name__ == "__main__":
    main()
