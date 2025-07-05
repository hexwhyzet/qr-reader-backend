from django.urls import path
from tg_bot.views import link_telegram

urlpatterns = [
    path("link-telegram/", link_telegram, name="link_telegram"),
]