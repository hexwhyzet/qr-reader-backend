from food.models import Dish, Order, Feedback, AllowedDish
from django.urls import path, reverse
from django.shortcuts import render, redirect
from food.models import Order
from django.utils import timezone
from food.services.order_statistics import OrderService
from myapp.admin_mixins import CustomAdmin
from datetime import timedelta
from django import forms
from django.db import IntegrityError


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
    
class AllowedDishForm(forms.Form):
    dishes = forms.ModelMultipleChoiceField(
        queryset=Dish.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Блюда",
        required=False,
    )
    
    def __init__(self, *args, **kwargs):
        self.date = kwargs.pop('date', None)
        super().__init__(*args, **kwargs)

        if self.date:
            existing_dishes = AllowedDish.objects.filter(date=self.date).values_list('dish_id', flat=True)
            self.fields['dishes'].initial = existing_dishes

    def save(self, commit=True):
        date = self.date
        selected_dishes = self.cleaned_data['dishes']
        existing_dishes = AllowedDish.objects.filter(date=date)

        
        existing_dish_ids = set(existing_dishes.values_list('dish_id', flat=True))
        selected_dish_ids = set(selected_dishes.values_list('id', flat=True))

        # Определяем блюда для добавления и удаления
        to_add = selected_dish_ids - existing_dish_ids
        to_remove = existing_dish_ids - selected_dish_ids

        
        for dish_id in to_add:
            try:
                if commit:
                    AllowedDish.objects.create(dish_id=dish_id, date=date)
            except IntegrityError:
                pass
        if commit:
            AllowedDish.objects.filter(dish_id__in=to_remove, date=date).delete()
    

class AllowedDishAdmin(CustomAdmin):
    list_display = ('dish', 'date')
    list_filter = ('date',)
    change_list_template = 'admin/order/change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add_menu/', self.admin_site.admin_view(self.batch_add_menu), name='add_menu'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """
        Представление для отображения блюд на 7 дней начиная с выбранной даты.
        """
        extra_context = extra_context or {}
        extra_context['show_weekly_statistics'] = True
        extra_context['show_weekly_view_button'] = True
        
        
        selected_date = request.GET.get('date')
        if selected_date:
            base_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
        else:
            base_date = timezone.now().date()

        days = [(base_date + timedelta(days=i)) for i in range(7)]

        dishes_by_date = [
            {
                'day': day,
                'dishes': AllowedDish.objects.filter(date=day),
            }
            for day in days
        ]

        extra_context['dishes_by_date'] = dishes_by_date
        
        return super().changelist_view(request, extra_context=extra_context)
    
    
    def batch_add_menu(self, request):
        selected_date = request.GET.get('date')
        if selected_date:
            base_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
        else:
            base_date = timezone.now().date()
        
        if request.method == 'POST':
            form = AllowedDishForm(request.POST, date=base_date)
            if form.is_valid():
                form.save()
                admin_url = reverse('admin:food_alloweddish_changelist')
                return redirect(admin_url)
        else:
            form = AllowedDishForm(date=base_date)
        
        context = {
            'date': base_date,
            'form': form
        }
        return render(request, 'admin/add_menu.html', context)


def register_food_admin(site):
    site.register(Dish)
    site.register(Order, OrderAdmin)
    site.register(Feedback, FeedbackModelAdmin)
    site.register(AllowedDish, AllowedDishAdmin)
