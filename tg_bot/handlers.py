from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import secrets
from django.utils import timezone
from tg_bot.models import TelegramLoginToken
from django.urls import reverse
from django.conf import settings
from asgiref.sync import sync_to_async


@sync_to_async
def create_token_entry(token, telegram_user_id):
    return TelegramLoginToken.objects.create(
        token=token,
        telegram_user_id=telegram_user_id,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user_id = update.effective_user.id

    token = secrets.token_urlsafe(32)

    await create_token_entry(token, telegram_user_id)

    url = f"{settings.DOMAIN}{reverse('link_telegram')}?token={token}"

    await update.message.reply_text(
        f"Привет! Для подключения уведомлений перейди по ссылке и войди в свой аккаунт:\n\n{url}",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
