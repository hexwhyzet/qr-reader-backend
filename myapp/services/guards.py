from myapp.models import Guard


def get_guard(guard_code):
    return Guard.objects.get(code=guard_code)
