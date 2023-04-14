from logging import warning

from django.apps import AppConfig

# use this because the name of app depends on from where django-orm is used
from web_app.web_app.settings import bot_web_app_name


class HuddleServiceBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = bot_web_app_name
