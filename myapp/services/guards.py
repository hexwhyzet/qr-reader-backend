from myapp.models import Guard


def get_guard(guard_code):
    return Guard.objects.get(code=guard_code)


def get_guards():
    return Guard.objects.all()


def get_guard_by_guard_id(guard_id):
    return Guard.objects.get(id=guard_id)


def get_manager_guards(user):
    if user.is_superuser or user.groups.filter(name='Senior Managers').exists():
        return Guard.objects.all()
    elif user.groups.filter(name='Managers').exists():
        return Guard.objects.filter(managers=user)
    return []
