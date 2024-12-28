from django.contrib.auth.models import Group


class CustomGroup:
    name = None
    verbose_name = None

    def get_object(self):
        return Group.objects.get(name=self.name)


class QRManager(CustomGroup):
    name = "qr_manager"
    verbose_name = "QR Manager"


class QRGuard(CustomGroup):
    name = "qr_guard"
    verbose_name = "QR Guard"


class UserManager(CustomGroup):
    name = "user_manager"
    verbose_name = "User Manager"
    
class CanteenManager(CustomGroup):
    name = "canteen_manager"
    verbose_name = "Canteen Manager"
    
class CanteenEmployee(CustomGroup):
    name = "canteen_employee"
    verbose_name = "Canteen Employee"
