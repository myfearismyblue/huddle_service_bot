from django.contrib import admin

from .models import Service, Subscription, TelegramUser, SubscriptionAlias


@admin.register(SubscriptionAlias)
class SubscriptionAliasAdmin(admin.ModelAdmin):
    list_display = ['alias', 'subscription', 'get_service',]

    def get_service(self, obj):
        return obj.subscription.service

    get_service.short_description = Service._meta.verbose_name


class SubscriptionAliasInline(admin.TabularInline):
    model = SubscriptionAlias


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscription_token', 'service',]
    inlines = [SubscriptionAliasInline]


class SubscriptionInline(admin.TabularInline):
    model = Subscription


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['service_token',]
    inlines = [SubscriptionInline]


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', ]

