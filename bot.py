import os
import json
import logging
from aiohttp import web
from botx import Bot, IncomingMessage, HandlerCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== КОНФИГ =====
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
BOT_HOST = os.getenv("BOT_HOST", "0.0.0.0")
BOT_PORT = int(os.getenv("BOT_PORT", "8000"))
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://skylinegtr030-web.github.io/max-bot-miniapp/")

# Два получателя уведомлений (номера телефонов аккаунтов в МАКС)
NOTIFY_RECIPIENTS = [
    os.getenv("NOTIFY_1", "89213734287"),   # первый получатель
    os.getenv("NOTIFY_2", ""),               # второй получатель - задай через .env NOTIFY_2=номер
]

collector = HandlerCollector()


@collector.command("/start", description="Начать")
async def start_handler(message: IncomingMessage, bot: Bot) -> None:
    """Приветствие и кнопка открытия Mini App."""
    await bot.answer_message(
        body=(
            "Привет! Я бот MAKC.\n"
            f"Нажмите кнопку ниже, чтобы открыть Mini App и оставить заявку:\n"
            f"{MINI_APP_URL}"
        ),
        message=message,
    )


@collector.command("/help", description="Помощь")
async def help_handler(message: IncomingMessage, bot: Bot) -> None:
    """Список доступных команд."""
    await bot.answer_message(
        body=(
            "Доступные команды:\n"
            "/start — начало работы\n"
            "/help — эта справка\n"
            "/app — открыть Mini App"
        ),
        message=message,
    )


@collector.command("/app", description="Открыть Mini App")
async def app_handler(message: IncomingMessage, bot: Bot) -> None:
    """Ссылка на Mini App."""
    await bot.answer_message(
        body=f"Ссылка на Mini App: {MINI_APP_URL}",
        message=message,
    )


async def submit_handler(request: web.Request) -> web.Response:
    """
    POST /submit — принимает данные формы из Mini App
    и пересылает уведомление двум получателям через бота.
    """
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "invalid JSON"}, status=400)

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    service = data.get("service", "").strip()
    comment = data.get("comment", "").strip()

    if not name or not phone or not service:
        return web.json_response({"ok": False, "error": "missing fields"}, status=422)

    service_labels = {
        "Konsultatsiya": "Консультация",
        "Zakaz": "Заказ",
        "Podderzhka": "Поддержка",
        "Drugoe": "Другое",
    }
    service_ru = service_labels.get(service, service)

    text = (
        f"\U0001F4CB Новая заявка из Mini App\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"\U0001F464 Имя: {name}\n"
        f"\U0001F4DE Телефон: {phone}\n"
        f"\U0001F6D2 Услуга: {service_ru}\n"
        f"\U0001F4AC Комментарий: {comment if comment else '—'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )

    bot: Bot = request.app["bot"]
    errors = []

    for recipient in NOTIFY_RECIPIENTS:
        if not recipient:
            continue
        try:
            await bot.send_message(
                body=text,
                chat_id=recipient,
            )
            logger.info(f"Notification sent to {recipient}")
        except Exception as e:
            logger.error(f"Failed to send to {recipient}: {e}")
            errors.append(str(e))

    if errors:
        return web.json_response({"ok": False, "error": "; ".join(errors)}, status=500)

    return web.json_response({"ok": True})


async def make_app() -> web.Application:
    bot = Bot(collectors=[collector], bot_accounts=[{"token": BOT_TOKEN}])
    app = web.Application()
    app["bot"] = bot

    app.router.add_post("/submit", submit_handler)
    app.router.add_get("/", lambda r: web.Response(text="MAKC Bot is running"))

    # Отдаём index.html (для локальной разработки)
    app.router.add_static("/static", path=".", name="static")

    return app


if __name__ == "__main__":
    import asyncio
    app = asyncio.get_event_loop().run_until_complete(make_app())
    web.run_app(app, host=BOT_HOST, port=BOT_PORT)
    logger.info(f"Bot running on {BOT_HOST}:{BOT_PORT}")
