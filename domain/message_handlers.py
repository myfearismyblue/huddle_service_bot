from asyncio import sleep
from dataclasses import dataclass
from typing import Iterable, List, Protocol, Tuple, Set, Union, Dict, Any, TypeVar, Coroutine

from aiogram import types


@dataclass
class SubscriptionRequest:
    service: str  # service with api
    subscription_token: str  # id, domain, group_id etc. to use with the service
    tg_user_id: int  # telegram user id


@dataclass
class BotPost:
    """DTO to be given to handler to send user"""
    text: str
    photo_urls: List[str]

# Custom JSON type to clarify various methods return
JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


# Type for a str becoming subscription alias
Alias = TypeVar('Alias', bound=str)


# The type fpr user commands
CommandType = TypeVar('CommandType')


class IGrabber(Protocol):
    """
    Responsible for querying service api and preparing answer
    """

    def handle(self, subscription_request: SubscriptionRequest) -> BotPost:
        ...

    def query(self, subscription_request: SubscriptionRequest) -> JSONType:
        ...

    def represent_response(self, subscription_request: SubscriptionRequest, data: JSONType) -> BotPost:
        ...


class IParser(Protocol):
    """Resolves user's message into reliable commands"""

    def parse(self, text: str) -> Iterable[CommandType]:
        ...


class AbstractAliasRepo(Protocol):
    """Abstract repo to determine subscription alias managing interface"""
    def get_subscription_info_by(self, alias: str) -> Tuple[str, str]:  # FIXME: consider return type
        """Returns service services and subscription token by alias"""
        ...

    def all_aliases_as_set(self) -> Set[str]:
        """Returns all stored aliases as set"""
        ...


class ISubscriptionRequestFactory(Protocol):
    def __init__(self, repo: AbstractAliasRepo) -> None:
        """Need to know where to get info about subscriptions"""
        ...

    def get_subscription_request_pool(self, commands: Iterable[CommandType], tg_user_id: int) -> Iterable[SubscriptionRequest]:
        """
        Creates an iterable of SubscriptionRequest objects which are corresponds to the given commands
        from one telegram user
        """
        ...


class MessageControllerFactory:
    def __call__(self, *args, **kwargs) -> Coroutine:
        message: types.Message = args[0]
        return self.listen_message_controller(message)

    def __init__(self, parser: IParser,
                       subscription_request_factory: ISubscriptionRequestFactory,
                       grabber: IGrabber):
        self._parser = parser
        self._subscription_request_factory = subscription_request_factory
        self._grabber = grabber

    async def message_controller(self, message: types.Message):
        """
        Fetches a list of BotPosts from handler and forms answer for each BotPost.
        Answers with photos and text if exists"""
        user_text: str = message.text
        tg_user_id: int = message.from_user.id
        parsed_commands: Iterable[Alias] = self._parser.parse(user_text)
        subscription_requests: Iterable[SubscriptionRequest] = \
            self._subscription_request_factory.get_subscription_request_pool(parsed_commands, tg_user_id)

        responses: List[BotPost] = []
        [responses.append(self._grabber.handle(_)) for _ in subscription_requests]

        for resp in responses:
            media = types.MediaGroup()
            for url in resp.photo_urls:
                media.attach_photo(url)
            if resp.photo_urls:
                await message.answer_media_group(media)
            await message.answer(resp.text)

    async def listen_message_controller(self, message: types.Message, timerefresh: int = 20):
        """
        Responsible for a continuous listening for new subscriptions' posts
        timerefresh: int period in seconds between services grabbing
        """
        assert message.text.startswith('/listen')
        user_text: str = message.text
        tg_user_id: int = message.from_user.id
        parsed_commands: Iterable[Alias] = self._parser.parse(user_text)
        subscription_requests: Iterable[SubscriptionRequest] = \
            self._subscription_request_factory.get_subscription_request_pool(parsed_commands, tg_user_id)
        while True:
            responses: List[BotPost] = []
            [responses.append(self._grabber.handle(_)) for _ in subscription_requests]

            for resp in responses:
                media = types.MediaGroup()
                for url in resp.photo_urls:
                    media.attach_photo(url)
                if resp.photo_urls:
                    await message.answer_media_group(media)
                await message.answer(resp.text)
            await sleep(timerefresh)
