from django.db.models import Count

from myapp.models import Round, Guard


def deactivate_rounds(guard: Guard):
    Round.objects.filter(guard=guard).update(is_active=False)
    Round.objects.annotate(num_visits=Count('visits')).filter(num_visits=0).delete()


def create_round(guard: Guard):
    return Round.objects.create(guard=guard)


def get_latest_round(guard: Guard):
    return Round.objects.filter(guard=guard).latest('created_at')
