from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from tg_bot import handlers

class Command(BaseCommand):
    help = "Запуск Telegram-бота"

    def handle(self, *args, **kwargs):
        import os
        from django.conf import settings

        BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or settings.TELEGRAM_BOT_TOKEN

        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", handlers.start))
        app.run_polling()
