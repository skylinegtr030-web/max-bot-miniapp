import os
import logging
from aiohttp import web
from botx import Bot, IncomingMessage, HandlerCollector

# Настройка логгинга
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфиг
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
BOT_HOST = os.getenv("BOT_HOST", "0.0.0.0")
BOT_PORT = int(os.getenv("BOT_PORT", "8000"))
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://skylinegtr030-web.github.io/max-bot-miniapp/")

collector = HandlerCollector()


@collector.command("/start", description="Начать")
async def start_handler(message: IncomingMessage, bot: Bot) -> None:
    """Приветствие и кнопка открытия Mini App."""
    await bot.answer_message(
        body="Добро пожаловать! Нажмите кнопку, чтобы открыть Mini App.",
        message=message,
    )


@collector.command("/help", description="Помощь")
async def help_handler(message: IncomingMessage, bot: Bot) -> None:
    """Список доступных команд."""
    await bot.answer_message(
        body=(
            "Доступные команды:\n"
            "/start — начальное приветствие\n"
            "/help — эта справка\n"
            "/app — открыть Mini App\n"
        ),
        message=message,
    )


@collector.command("/app", description="Открыть Mini App")
async def app_handler(message: IncomingMessage, bot: Bot) -> None:
    """Отправляет ссылку на Mini App."""
    await bot.answer_message(
        body=f"Откройте приложение: {MINI_APP_URL}",
        message=message,
    )


def main():
    bot = Bot(
        collectors=[collector],
        bot_accounts=[
            {"host": BOT_HOST, "secret_key": BOT_TOKEN},
        ],
    )

    app = web.Application()
    bot.include_router(app.router)

    logger.info("Бот запущен на %s:%s", BOT_HOST, BOT_PORT)
    web.run_app(app, host=BOT_HOST, port=BOT_PORT)


if __name__ == "__main__":
    main()
