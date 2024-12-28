from django.db import models
from django.contrib.auth.models import User

class Dish(models.Model):
    CATEGORY_CHOICES = [
        ('first_course', 'Первое блюдо'),
        ('side_dish', 'Гарнир'),
        ('main_course', 'Второе блюдо'),
        ('salad', 'Салат'),
    ]
    name = models.CharField(max_length=255, verbose_name='Название блюда')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Тип блюда')
    photo = models.ImageField(upload_to='dish_photos/', verbose_name='Фотография блюда', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"

    def __str__(self):
        return self.name
    
class OrderStatus(models.TextChoices):
    PENDING = 'Pending', 'Ожидает'
    APPROVED = 'Approved', 'Подтверждено'
    CANCELED = 'Canceled', 'Отменено'
    COMPLETED = 'Completed', 'Завершено'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name='Блюдо')
    cooking_time = models.DateField(verbose_name='Дата готовки блюда')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий к заказу')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name='Статус заказа'
    )
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Order by {self.user} for {self.dish}"

class Feedback(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name='Блюдо')
    comment = models.TextField(verbose_name='Отзыв')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Feedback on {self.dish}"
    