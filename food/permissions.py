from rest_framework import permissions

class CanAccessOrder(permissions.BasePermission):
    """
    Позволяет создавать или редактировать закза только владельцу, не позже чем за сутки до готовки;
    """
    def has_object_permission(self, request, view, order):
        return order.user == request.user
    
    
class CanAccessOrderStats(permissions.BasePermission):
    """
    Разрешение для доступа к агрегированным данным о заказах.
    Проверяет, что у пользователя есть роль 'Canteen_manager'.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='canteen_manager').exists()