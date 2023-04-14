from django.db import models

class Service(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    service_token = models.CharField(max_length=255, unique=True, verbose_name='Service')

    def __str__(self):
        return f'{self.service_token}'

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['service_token',]


class Subscription(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    subscription_token = models.CharField(max_length=255, unique=True, verbose_name = 'Subscription')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='subscriptions')

    def __str__(self):
        return f'{self.subscription_token}'

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['subscription_token',]


class TelegramUser(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    telegram_id = models.IntegerField(unique=True, verbose_name = 'TelegramUser')
    subscriptions = models.ManyToManyField(Subscription, related_name='telegram_users', through='LastPostForUser')
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name='Name')

    def __str__(self):
        return f'{self.telegram_id}, {self.name}'

    class Meta:
        verbose_name = 'TelegramUser'
        verbose_name_plural = 'TelegramUsers'
        ordering = ['telegram_id',]


class SubscriptionAlias(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    alias = models.CharField(max_length=16, verbose_name='Alias')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='aliases')

    def __str__(self):
        return f'{self.alias}'

    class Meta:
        verbose_name = 'Alias'
        verbose_name_plural = 'Aliases'
        ordering = ['subscription',]


class LastPostForUser(models.Model):
    subscription = models.ForeignKey(Subscription, null=False, blank=False, on_delete=models.CASCADE)
    telegram_user = models.ForeignKey(TelegramUser, blank=False, null=False, on_delete=models.CASCADE)
    last_post_id = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f'Last post for {self.telegram_user.name} in {self.subscription}: {self.last_post_id}'

    class Meta:
        verbose_name = 'Last post'
        verbose_name_plural = 'Last posts'
        ordering = ['telegram_user',]
