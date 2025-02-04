from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    
class AllowedDish(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name='Блюдо')
    date = models.DateField(verbose_name='Дата')

    class Meta:
        verbose_name = "Меню"
        verbose_name_plural = "Меню"
        unique_together = ('dish', 'date')

    def __str__(self):
        return f"{self.dish.name} ({self.date})"
    
class OrderStatus(models.TextChoices):
    PENDING = 'Pending', 'Ожидает'
    APPROVED = 'Approved', 'Подтверждено'
    CANCELED = 'Canceled', 'Отменено'
    COMPLETED = 'Completed', 'Завершено'

class Order(models.Model):
    is_deleted = models.BooleanField(default=False, verbose_name='Удалён')
    deletion_reason = models.TextField(null=True, blank=True, verbose_name='Причина удаления')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Время удаления')
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
    
    def delete(self, reason=None, *args, **kwargs):
        self.is_deleted = True
        self.deletion_reason = reason
        self.deleted_at = timezone.now()
        self.save()
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ блюда: {self.dish}, для: {self.user}"

class Feedback(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name='Блюдо')
    comment = models.TextField(verbose_name='Отзыв')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_read = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        if not self.is_read:
            return f'[НЕ ПРОЧИТАНО] отзыв на {self.dish}'
        return f"Отзыв на {self.dish}"
    