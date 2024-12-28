from django.contrib import admin
from food.models import Dish, Order, Feedback

class FeedbackModelAdmin(admin.ModelAdmin):
    exclude = ['user',]

admin.site.register(Dish)
admin.site.register(Order)
admin.site.register(Feedback, FeedbackModelAdmin)