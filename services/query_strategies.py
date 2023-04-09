from typing import Protocol

from domain.message_handlers import SubscriptionRequest
from tokens import VK_API_TOKEN, VK_USER_ID


class QueryStrategy(Protocol):
    """Abstract protocol to handle concrete strategies of services' querying"""

    def get_query(self, subscription_request: SubscriptionRequest) -> str:
        ...


class VKQueryStrategy:
    """Strategy to query vk.com api"""

    @staticmethod
    def get_query(subscription_request: SubscriptionRequest) -> str:
        domain_id: str = subscription_request.subscription_token  # should be group name
        vk_query = f"https://api.vk.com/method/wall.get?access_token={VK_API_TOKEN}&user_id={VK_USER_ID}&" \
                   f"domain={domain_id}&count={1}&v=5.84"
        return vk_query
