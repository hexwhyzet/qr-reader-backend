# Generated by Django 5.0.4 on 2024-12-01 03:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_message'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'verbose_name': 'Сообщение', 'verbose_name_plural': 'Сообщение'},
        ),
    ]