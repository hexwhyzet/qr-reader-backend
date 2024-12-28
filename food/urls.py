from django.urls import path, include
from rest_framework.routers import DefaultRouter
from food.views import DishViewSet, OrderViewSet, FeedbackViewSet

router = DefaultRouter()
router.register('dishes', DishViewSet)
router.register('orders', OrderViewSet, basename='Заказы')
router.register('feedback', FeedbackViewSet)

urlpatterns = [
    path('', include(router.urls)),
]