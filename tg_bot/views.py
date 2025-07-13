from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from tg_bot.models import TelegramLoginToken

@login_required
def link_telegram(request):
    token = request.GET.get("token")
    if not token:
        return HttpResponse("Токен не указан", status=400)

    login_token = TelegramLoginToken.objects.filter(token=token, is_used=False).first()
    if not login_token:
        return HttpResponse("Токен недействителен или уже использован", status=400)

    request.user.telegram_user_id = login_token.telegram_user_id
    request.user.save()

    login_token.is_used = True
    login_token.save()

    return HttpResponse("Подписка на уведомления успешно оформлена. Можно закрыть это окно.")
