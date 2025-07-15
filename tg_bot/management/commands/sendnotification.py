from django.core.management.base import BaseCommand, CommandError
from telegram import Bot
from telegram.constants import ParseMode
import os
from django.conf import settings
import asyncio

class Command(BaseCommand):
    help = "Отправка уведомления Telegram-пользователю"

    def add_arguments(self, parser):
        parser.add_argument("telegram_user_id", type=int, help="Telegram ID пользователя")
        parser.add_argument("message", type=str, help="Текст сообщения")

    def handle(self, *args, **options):
        telegram_user_id = options["telegram_user_id"]
        message = options["message"]

        BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or settings.TELEGRAM_BOT_TOKEN
        if not BOT_TOKEN:
            raise CommandError("Не задан TELEGRAM_BOT_TOKEN в переменных окружения или settings.py")

        bot = Bot(token=BOT_TOKEN)

        async def send():
            await bot.send_message(
                chat_id=telegram_user_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            self.stdout.write(
                self.style.SUCCESS(f"Сообщение отправлено Telegram ID {telegram_user_id}")
            )

        try:
            asyncio.run(send())
        except Exception as e:
            raise CommandError(f"Ошибка при отправке: {e}")
