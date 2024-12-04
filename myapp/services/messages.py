from myapp.models import Message


def create_message(guard, visit, text):
    return Message.objects.create(guard=guard, visit=visit, text=text)


def messages_by_user(user):
    if user.is_superuser or user.groups.filter(name='Senior Managers').exists():
        return Message.objects.filter(is_seen=False).all()
    elif user.groups.filter(name='Managers').exists():
        return Message.objects.filter(guard__managers=user, is_seen=False)
    return []
