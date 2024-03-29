from django.contrib import admin

from .models import Service, Subscription, TelegramUser, SubscriptionAlias, LastPostForUser


class TelegramUserInline(admin.TabularInline):
    model = Subscription.telegram_users.through
    extra = 1


class SubscriptionAliasInline(admin.TabularInline):
    model = SubscriptionAlias
    extra = 1


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 1


class LastPostForUserInline(admin.TabularInline):
    model = LastPostForUser
    extra = 1


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscription_token', 'service', ]
    inlines = [SubscriptionAliasInline,
               TelegramUserInline,
               ]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['service_token', ]
    inlines = [SubscriptionInline, ]


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'name', 'get_subscriptions', ]
    inlines = [LastPostForUserInline, ]

    def get_subscriptions(self, obj):
        return [_[1] for _ in obj.subscriptions.values_list()]

    get_subscriptions.short_description = Subscription._meta.verbose_name_plural


@admin.register(SubscriptionAlias)
class SubscriptionAliasAdmin(admin.ModelAdmin):
    list_display = ['alias', 'subscription', 'get_service', ]

    def get_service(self, obj):
        return obj.subscription.service

    get_service.short_description = Service._meta.verbose_name