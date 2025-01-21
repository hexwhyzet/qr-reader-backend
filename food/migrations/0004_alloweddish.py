# Generated by Django 5.0.4 on 2025-01-20 23:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0003_alter_order_deleted_at_alter_order_deletion_reason_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllowedDish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата')),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='food.dish', verbose_name='Блюдо')),
            ],
            options={
                'verbose_name': 'Разрешённое блюдо',
                'verbose_name_plural': 'Разрешённые блюда',
                'unique_together': {('dish', 'date')},
            },
        ),
    ]