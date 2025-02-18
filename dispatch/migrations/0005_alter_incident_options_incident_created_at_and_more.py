# Generated by Django 5.0.4 on 2025-02-11 13:06

import dispatch.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispatch', '0004_alter_incident_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='incident',
            options={'verbose_name': 'Инцидент', 'verbose_name_plural': 'Инциденты'},
        ),
        migrations.AddField(
            model_name='incident',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='audiomessage',
            name='audio',
            field=models.FileField(storage=dispatch.models.S3MediaStorage(), upload_to=dispatch.models.PathAndRename('audios')),
        ),
        migrations.AlterField(
            model_name='duty',
            name='is_opened',
            field=models.BooleanField(default=False, verbose_name='Открыт ли'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opened_incident', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='description',
            field=models.TextField(verbose_name='Описание инцидента'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='is_critical',
            field=models.BooleanField(default=False, help_text='Автоматически выставляется, если ни один из уровней не справился с выполнением', verbose_name='Критичный'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='level',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Уровень'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Имя инцидента'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='point',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incidents', to='dispatch.dutypoint', verbose_name='Точка диспетчеризации'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='responsible_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='responsible_incidents', to=settings.AUTH_USER_MODEL, verbose_name='Ответственный дежурный'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='status',
            field=models.CharField(choices=[('opened', 'В работе'), ('closed', 'Выполнено'), ('force_closed', 'Ненадлежащее выполнение')], default='opened', max_length=12, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='photomessage',
            name='photo',
            field=models.ImageField(storage=dispatch.models.S3MediaStorage(), upload_to=dispatch.models.PathAndRename('photos')),
        ),
        migrations.AlterField(
            model_name='videomessage',
            name='video',
            field=models.FileField(storage=dispatch.models.S3MediaStorage(), upload_to=dispatch.models.PathAndRename('videos')),
        ),
    ]
