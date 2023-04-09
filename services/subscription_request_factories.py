from typing import Iterable

from domain.message_handlers import AbstractAliasRepo, CommandType, SubscriptionRequest


class SubscriptionRequestFactory:
    """Responsible for creating SubscriptionRequest object"""
    def __init__(self, repo: AbstractAliasRepo) -> None:
        self._storage: AbstractAliasRepo = repo

    def get_subscription_request_pool(self, commands: Iterable[CommandType],
                                      tg_user_id: int) -> Iterable[SubscriptionRequest]:
        """
        Creates an iterable of SubscriptionRequest objects which are corresponds to the given commands
        from one telegram user"""

        return [self._create_subscription_request_by_(command, tg_user_id) for command in commands]

    def _create_subscription_request_by_(self, command: CommandType, tg_user_id: int) -> SubscriptionRequest:
        """Creates a single SubscriptionRequest object using the given command and telegram user id"""
        service, subscription = self._storage.get_subscription_info_by(command)
        # FIXME: is command and alias are the same thing?
        tg_user_id = int(tg_user_id)
        return SubscriptionRequest(service, subscription, tg_user_id)
