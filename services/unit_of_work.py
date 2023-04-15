from typing import Optional

import domain

DEFAULT_DJANGO_SETTINGS = "web_app.web_app.settings"


class DjangoUoW(domain.AbstractUoW):
    import django

    def __init__(self,
                 repository: type(domain.AbstractAliasRepo),
                 settings: str = DEFAULT_DJANGO_SETTINGS,
                 ):
        self._django_settings: str = settings
        self.storage_cls: type[domain.AbstractAliasRepo] = repository
        self.__storage: Optional[domain.AbstractAliasRepo] = None

    @property
    def storage(self) -> domain.AbstractAliasRepo:
        if self.__storage is None:
            raise AssertionError(f'Repository should be managed only with context manager')
        return self.__storage

    def __enter__(self) -> domain.AbstractUoW:
        import os
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", self._django_settings)
        os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "True")
        self.django.setup()
        from web_app.huddle_service_bot import models
        model = getattr(models, self.storage_cls.model_name)
        self.__storage = self.storage_cls(model)
        return super().__enter__()

    def __exit__(self, *args):
        self.django.db.close_old_connections()
