from rest_framework import serializers, fields
from food.models import Dish, Order, Feedback
from django.utils import timezone


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=fields.CurrentUserDefault())
    status = serializers.ReadOnlyField()
    
    def validate_cooking_time(self, value):
        old_cooking_time = self.instance.cooking_time if self.instance else None
        
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)

        if old_cooking_time and old_cooking_time < tomorrow:
            raise serializers.ValidationError("Заказ нельзя редактировать менее чем за сутки до даты готовки.")
        if value < tomorrow:
            raise serializers.ValidationError("Дату готовки нельзя назначить ранее чем на завтрашний день.")
        
        return value
    
    def validate(self, data):
        cooking_time = data.get('cooking_time', None)

        if cooking_time:
            self.validate_cooking_time(cooking_time)
        
        return data

    class Meta:
        model = Order
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'