from typing import Type

import requests

from domain.message_handlers import SubscriptionRequest, BotPost, JSONType
from services.query_strategies import QueryStrategy
from services.represent_strategies import RepresentStrategy
from services.strategy_registers import QueryStrategyRegister, RepresentStrategyRegister


class Grabber:
    def __init__(self, query_strategy_register: Type[QueryStrategyRegister],
                       represent_strategy_register: Type[RepresentStrategyRegister]):
        self._query_strategy_register = query_strategy_register
        self._represent_strategy_register = represent_strategy_register

    def handle(self, subscription_request: SubscriptionRequest) -> BotPost:
        data: JSONType = self.query(subscription_request)
        return self.represent_response(subscription_request, data)

    def query(self, subscription_request: SubscriptionRequest) -> JSONType:
        """Chooses concrete query preparing strategy by subscription service and query the service"""
        strategy: QueryStrategy = self._query_strategy_register.get_strategy_by(subscription_request)
        query: str = strategy.get_query(subscription_request)
        response = requests.get(query)
        return response.json()

    def represent_response(self, subscription_request: SubscriptionRequest, data: JSONType) -> BotPost:
        """Represents fetched data as a BotPost. Uses subscription_request to choose a strategy of preparation"""
        represent_strategy: RepresentStrategy = self._represent_strategy_register.get_strategy_by(subscription_request)
        return represent_strategy.represent(subscription_request, data)