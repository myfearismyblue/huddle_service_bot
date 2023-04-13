# Generated by Django 4.2 on 2023-04-13 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huddle_service_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ['service_token'], 'verbose_name': 'Service', 'verbose_name_plural': 'Services'},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ['subscription_token'], 'verbose_name': 'Subscription', 'verbose_name_plural': 'Subscriptions'},
        ),
        migrations.AlterModelOptions(
            name='telegramuser',
            options={'ordering': ['telegram_id'], 'verbose_name': 'TelegramUser', 'verbose_name_plural': 'TelegramUsers'},
        ),
    ]
