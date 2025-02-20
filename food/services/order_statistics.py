from django.db.models import Count
from django.utils import timezone
from food.models import Order

class OrderService:
    @staticmethod
    def calc_statistic(date=None):
        if not date:
            date = timezone.now().date()

        aggregate_data = Order.objects.filter(cooking_time=date, is_deleted=False) \
                                      .values('dish__name', 'dish__id') \
                                      .annotate(total_orders=Count('id'))

        result = []
        for item in aggregate_data:
            result.append({
                'dish': item['dish__name'],
                'total_orders': item['total_orders'],
            })
        return result