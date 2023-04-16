from logging import warning
from typing import Tuple, Set

from django.db import models

from domain.message_handlers import AbstractSubscriptionRepo, AbstractAliasRepo


class AliasSubscriptionsRepo(AbstractAliasRepo):
    """Concrete implementation of AbstractAliasRepo"""
    model_name: str = 'SubscriptionAlias'

    def __init__(self, model: models.Model):
        self._model = model

    def get_subscription_info_by(self, alias: str) -> Tuple[str, str]:  # FIXME: consider return type
        """Returns service domain and subscription token by alias"""
        assert isinstance(alias, str)
        all_aliases = self._model.objects.filter(alias__iexact=alias)
        if len(all_aliases) > 1:
            warning(f'Found more then a single match to a given {alias=}: {all_aliases}.')
        elif len(all_aliases) == 0:
            assert False, f'Have no such command: {alias}'
        subscription = all_aliases[0].subscription
        service = subscription.service
        return service.service_token, subscription.subscription_token

    def all_aliases_as_set(self) -> Set[str]:
        """Return all stored aliases as set"""
        return {_.alias for _ in self._model.objects.all()}


class SubscriptionRepo(AbstractSubscriptionRepo):
    """Repository responsible for managing Subscription django model """
    model_name = 'Subscription'

    def __init__(self, model: models.Model):
        self._model = model

    def get_all_subscriptions_as_set(self) -> Set[str]:
        return {_.subscription_token for _ in self._model.objects.all()}
