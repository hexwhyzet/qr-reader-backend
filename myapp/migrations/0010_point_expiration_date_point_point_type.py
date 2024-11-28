# Generated by Django 5.0.4 on 2024-11-30 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_remove_guard_manager_alter_guard_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='point',
            name='expiration_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата истечения'),
        ),
        migrations.AddField(
            model_name='point',
            name='point_type',
            field=models.CharField(choices=[('default', 'Обычная точка'), ('fire_extinguisher', 'Огнетушитель')], default='default', max_length=20, verbose_name='Тип точки'),
        ),
    ]