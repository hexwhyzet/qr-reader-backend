from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from food.models import Dish, Order, Feedback, AllowedDish
from food.serializers import DishSerializer, OrderSerializer, FeedbackSerializer, AllowedDishSerializer
from food.permissions import CanAccessOrder, CanAccessOrderStats
from food.services.order_statistics import OrderService


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    @action(detail=True, methods=['post'], url_path='upload-photo')
    def upload_photo(self, request, pk=None):
        instance = self.get_object()

        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        instance.photo = photo
        instance.save()
        return Response({'message': 'Image updated successfully'}, status=status.HTTP_200_OK)


class AllowedDishViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AllowedDishSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    def get_queryset(self):
        today = timezone.now().date()
        return AllowedDish.objects.filter(date__gte=today)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, CanAccessOrder]
    
    def get_queryset(self):
        today = timezone.now().date()
        return Order.objects.filter(user=self.request.user, is_deleted=False, cooking_time__gte=today)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        reason = request.data.get('reason', 'Причина не указана')
        instance.delete(reason=reason)
        return Response(
            {
                "detail": "Заказ удалён",
                "reason": reason
            },
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, CanAccessOrderStats])
    def aggregate_orders(self, request):
        """
        Возвращает агрегированную информацию по заказам за указанный день.
        Если параметр даты не указан, используется текущая дата.
        """
        date_str = request.query_params.get('date', None)
        
        if date_str:
            try:
                date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'detail': 'Неверный формат даты. Используйте YYYY-MM-DD.'}, status=400)
        else:
            date = timezone.now().date()
        
        aggregate_data = OrderService.calc_statistic(date)

        return Response(aggregate_data)


class RemovedOrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.filter(is_deleted=True)
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, CanAccessOrderStats]
    
    def get_queryset(self):
        today = timezone.now().date()
        return Order.objects.filter(is_deleted=True, cooking_time__gte=today)

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
