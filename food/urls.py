from django.urls import path, include
from rest_framework.routers import DefaultRouter
from food.views import (
    DishViewSet,
    OrderViewSet,
    RemovedOrderViewSet,
    FeedbackViewSet,
    AllowedDishViewSet
)

router = DefaultRouter()
router.register('dishes', DishViewSet)
router.register('orders', OrderViewSet, basename='Заказы')
router.register('removed_orders', RemovedOrderViewSet, basename='Удалённые заказы')
router.register('feedback', FeedbackViewSet)
router.register('allowed_dishes', AllowedDishViewSet, basename='Меню')

urlpatterns = [
    path('', include(router.urls)),
]