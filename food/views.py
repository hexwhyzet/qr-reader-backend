from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count
from food.models import Dish, Order, Feedback
from food.serializers import DishSerializer, OrderSerializer, FeedbackSerializer
from food.permissions import CanCreateOnly, CanAccessOrder, CanAccessOrderStats


class DishViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, CanAccessOrder]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
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
        
        aggregate_data = Order.objects.filter(created_at__date=date) \
                                      .values('dish__name', 'dish__id') \
                                      .annotate(total_orders=Count('id'),)
                                      
        result = []
        for item in aggregate_data:
            result.append({
                'dish': item['dish__name'],
                'total_orders': item['total_orders'],
            })
        
        return Response(result)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.none()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, CanCreateOnly]
