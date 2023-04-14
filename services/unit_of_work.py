from __future__ import annotations

from abc import ABC, abstractmethod

import domain
import repo


class AbstractUoW(ABC):
    storage: domain.AbstractAliasRepo

    def __enter__(self) -> AbstractUoW:
        return self

    @abstractmethod
    def __exit__(self, *args):
        ...


DEFAULT_DJANGO_SETTINGS = "web_app.web_app.settings"


class DjangoUoW(AbstractUoW):

    def __init__(self, settings: str = DEFAULT_DJANGO_SETTINGS, repository=repo.AliasSubscriptionsRepo()):
        self._django_settings: str = settings
        self.storage: domain.AbstractAliasRepo = repository

    def __enter__(self) -> AbstractUoW:
        import os
        import django
        self.django = django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", self._django_settings)
        django.setup()
        return super().__enter__()

    def __exit__(self, *args):
        self.django.db.close_old_connections()
