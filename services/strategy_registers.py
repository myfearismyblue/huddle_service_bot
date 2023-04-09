from typing import Dict, Tuple, Optional

from domain.message_handlers import SubscriptionRequest
from services.query_strategies import VKQueryStrategy, QueryStrategy
from services.represent_strategies import (RepresentStrategy,
                                           MilongaRepresentStrategy,
                                           OldclothersRepresentStrategy,
                                           KvartalRepresentStrategy)


class QueryStrategyRegister:
    """
    The register of various strategies to be used for creating query of services' api.
    Use .get_strategy_by(subscription_request) to get concrete strategy
    """

    _storage: Dict[str, QueryStrategy] = {'vk.com': VKQueryStrategy}

    @classmethod
    def get_strategy_by(cls, subscription_request: SubscriptionRequest) -> QueryStrategy:
        domain: str = subscription_request.service
        strategy: Optional[QueryStrategy] = cls._storage.get(domain)()
        if strategy:
            return strategy
        raise ValueError(f'Wrong SubscriptionRequest. The query strategy for domain: {domain} is not supported.')


class RepresentStrategyRegister:
    """
    The register of various strategies to be used for represent services' answers.
    Uses service's domain and subscription token as a key for
    Use .get_strategy_by(subscription_request) to get concrete strategy
        """
    _storage: Dict[Tuple[str, str], RepresentStrategy] = {('vk.com', 'milonga'): MilongaRepresentStrategy,
                                                          ('vk.com', 'oldclothers'): OldclothersRepresentStrategy,
                                                          ('vk.com', 'kvartal_tango'): KvartalRepresentStrategy,
                                                          }

    @classmethod
    def get_strategy_by(cls, subscription_request: SubscriptionRequest) -> RepresentStrategy:
        domain: str = subscription_request.service
        subscription: str = subscription_request.subscription_token
        strategy: Optional[RepresentStrategy] = cls._storage.get((domain, subscription))
        if strategy:
            return strategy
        raise ValueError(f'Wrong SubscriptionRequest. The strategy for: {domain, subscription} is not supported.')
