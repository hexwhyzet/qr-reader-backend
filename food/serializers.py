from rest_framework import serializers, fields
from food.models import Dish, Order, Feedback, AllowedDish
from django.utils import timezone


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'
        
class AllowedDishSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedDish
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=fields.CurrentUserDefault())
    
    def validate_cooking_time(self, value):
        old_cooking_time = self.instance.cooking_time if self.instance else None
        
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        week_end = timezone.now().date() + timezone.timedelta(days=7)

        if old_cooking_time and old_cooking_time < tomorrow:
            raise serializers.ValidationError("Заказ нельзя редактировать менее чем за сутки до даты готовки.")
        if value < tomorrow:
            raise serializers.ValidationError("Дату готовки нельзя назначить ранее чем на завтрашний день.")
        if value > week_end:
            raise serializers.ValidationError("Заказ нельзя сделать раньше чем за неделю.")
        
        return value
    
    def validate(self, data):
        cooking_time = data.get('cooking_time', None)
        dish = data.get('dish', None)
        user = data.get('user', None)

        if cooking_time:
            self.validate_cooking_time(cooking_time)

            if dish:
                allowed_dishes = AllowedDish.objects.filter(dish=dish, date=cooking_time)
                if not allowed_dishes.exists():
                    raise serializers.ValidationError(
                        f"Блюдо '{dish.name}' недоступно для заказа на {cooking_time}."
                    )
                    
        if Order.objects.filter(
            user=user,
            cooking_time=cooking_time,
            is_deleted=False,
            dish__category=dish.category
        ).exists():
            raise serializers.ValidationError(
                f"Уже заказано блюдо категории {dish.get_category_display()} на {cooking_time}"
            )

        return data

    class Meta:
        model = Order
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'