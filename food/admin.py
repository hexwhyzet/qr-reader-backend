from food.models import Dish, Order, Feedback
from django.urls import path
from django.shortcuts import render
from food.models import Order
from django.utils import timezone
from food.services.order_statistics import OrderService
from myapp.admin_mixins import CustomAdmin


class FeedbackModelAdmin(CustomAdmin):
    readonly_fields = ('is_read',)
    
    def get_unread_count(self):
        return Feedback.objects.filter(is_read=False).count()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)

        if obj and not obj.is_read:
            obj.is_read = True
            obj.save(update_fields=['is_read'])
        
        return super().change_view(request, object_id, form_url, extra_context)

    exclude = ['user',]
class OrderAdmin(CustomAdmin):
    change_list_template = 'admin/order/change_list.html'

    def changelist_view(self, request, extra_context=None):
        """
        Переопределяем метод changelist_view, чтобы добавить кнопку на страницу списка заказов.
        """
        extra_context = extra_context or {}
        extra_context['show_calc_statistics_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

    def calc_order_statistics_form(self, request):
        """
        Форма для выбора даты.
        """
        return render(request, 'admin/order/calc_statistics.html')

    def calc_statistics(self, request):
        """
        Кастомное действие для агрегирования заказов по выбранной дате.
        """
        date_str = request.GET.get('date', None)
        
        if date_str:
            try:
                date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.message_user(request, 'Неверный формат даты. Используйте YYYY-MM-DD.', level='error')
                return render(request, 'admin/order/calc_statistics.html')
        else:
            date = timezone.now().date()

        statistic = OrderService.calc_statistic(date)

        return render(request, 'admin/order/calc_statistics.html', {
            'statistics': statistic,
            'date': date,
        })

    def get_urls(self):
        """
        Добавляем кастомный URL для отображения формы выбора даты.
        """
        urls = super().get_urls()
        custom_urls = [
            path('orders-statistics/', self.admin_site.admin_view(self.calc_order_statistics_form), name='calc_order_statistics_form'),
            path('order-statistics-result/', self.admin_site.admin_view(self.calc_statistics), name='calc_order_statistics'),
        ]
        return custom_urls + urls

def register_food_admin(site):
    site.register(Dish)
    site.register(Order, OrderAdmin)
    site.register(Feedback, FeedbackModelAdmin)
