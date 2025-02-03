from myapp.models import VerboseUserDisplay


def get_all_users():
    return VerboseUserDisplay.objects.all()
