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

class SeniorUserManager(CustomGroup):
    name = "senior_user_manager"
    verbose_name = "Senior User Manager"

class CanteenManager(CustomGroup):
    name = "canteen_manager"
    verbose_name = "Canteen Manager"
    
class CanteenAdminManager(CustomGroup):
    name = "canteen_admin_manager"
    verbose_name = "Canteen Admin Manager"
    
class CanteenEmployee(CustomGroup):
    name = "canteen_employee"
    verbose_name = "Canteen Employee"
