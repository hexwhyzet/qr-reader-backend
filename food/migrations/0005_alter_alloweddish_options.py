# Generated by Django 5.0.4 on 2025-01-24 10:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0004_alloweddish'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alloweddish',
            options={'verbose_name': 'Меню', 'verbose_name_plural': 'Меню'},
        ),
    ]
