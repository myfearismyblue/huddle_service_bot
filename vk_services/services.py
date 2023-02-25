import json
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from logging import warning
from typing import Dict, List

import requests as requests

from aiogram import types

from .vk_container import domain, access_token, user_id
from .vk_exceptions import BadRequestException, NonRegularPostResponse, NotAppropriateContent


class GroupDomainNameAliases:
    """
    Alternative names for vk groups names
    Usage:
    {"group_name1": frozenset(["alias_1", "alias_2"]),
     "group_name2": frozenset(["alias_3", "alias_4"]),
    })
    """

    _storage = {"milonga": frozenset(["milonga", "mil"]),
                "oldclothers": frozenset(["old", "darom"]),
                "kvartal_tango": frozenset(["kv", ])
                }

    @classmethod
    def __setitem__(cls, key, value):
        cls._storage.__setitem__(key, value)

    @classmethod
    def __contains__(cls, item):
        return cls._storage.__contains__(item)

    @classmethod
    def __iter__(cls):
        return cls._storage.__iter__()

    @classmethod
    def __getitem__(cls, item):
        return cls._storage.__getitem__(item)

    @classmethod
    def as_list(cls) -> List[str]:
        """Returns all aliases defined in self._storage. Each element of the return is unique."""
        reverse_aliases = {v: k for k, v in cls._storage.items()}
        tmp = list(reverse_aliases.keys())
        vk_group_aliases = set()
        [vk_group_aliases.update(set_) for set_ in tmp]
        return list(vk_group_aliases)

    @classmethod
    def get_groups_by_alias(cls, alias: str) -> List[str]:
        """Founds group names by a given alias.
        Returns these names as list of strings"""
        assert isinstance(alias, str)
        ret = set()
        for group in cls._storage:
            if alias in cls._storage[group]:
                ret.update((group, ))

        return list(ret)


@dataclass
class BotPost:
    """DTO to be given to handler to send user"""
    text: str
    photo_urls: List[str]


class VKGroupGrabber:

    @classmethod
    def _build_vk_query(cls, domain_id: str):
        vk_query = f"{domain}/wall.get?access_token={access_token}&user_id={user_id}&" \
                   f"domain={domain_id}&count={1}&v=5.84"
        return vk_query

    @classmethod
    def _fetch_pretty_json(cls, vk_query, indent=4):
        """Fetches response and gets text as pretty json from it"""
        response = requests.get(vk_query)
        data = response.text
        json_string = json.dumps(json.loads(data), indent=indent, ensure_ascii=False).encode('utf8')
        return json_string

    @classmethod
    def _fetch_json(cls, vk_query):
        response = requests.get(vk_query)
        return response.json()

    @classmethod
    def prepare_query_and_grab_data(cls, alias: str):
        if alias not in GroupDomainNameAliases.as_list():
            raise ValueError(f'Wrong {alias=}')
        groups_names = GroupDomainNameAliases.get_groups_by_alias(alias)
        vk_query = cls._build_vk_query(groups_names[0])  # FIXME: only the first group
        data = cls._fetch_json(vk_query)
        return data

    @classmethod
    def presentate_grabbed_data(cls, alias: str, data) -> BotPost:
        groups_names = GroupDomainNameAliases.get_groups_by_alias(alias)
        prepare_strategy: VKAnswerPrepareBaseStrategy = \
            VKAnswerPrepareStrategyRegister.get_strategy_by_group_name(groups_names[0])
        post: BotPost = prepare_strategy.prepare_answer(data)
        return post


class VKAnswerPrepareBaseStrategy(ABC):
    """Base class for vk responses handle strategies"""
    @abstractmethod
    def prepare_answer(self, data: Dict) -> BotPost:
        ...


class MilongaPrepareStrategy(VKAnswerPrepareBaseStrategy):
    """In case of listening daily milongas group"""

    @classmethod
    def prepare_answer(cls, data: Dict) -> BotPost:
        try:
            group_resp: BotPost = cls._presentate_milongas_or_err(data)
        except (BadRequestException, NonRegularPostResponse) as e:
            warning(e)
            group_resp = BotPost(text='No result for milongas. See terminal log.', photo_urls=[])
        return group_resp

    @classmethod
    def _presentate_milongas_or_err(cls, data: Dict) -> BotPost:
        """Extract polling answers from post attachment, sorts with milonga rate and returns formatted string.
        If error occurred while responding or can't find milongas inside valid response raises corresponding exception
        """
        if 'error' in data:
            msg = data['error']['error_msg']
            raise BadRequestException(f'Error while requesting vk api: {msg}')
        try:
            # finds date of milonga by # char
            date_ends_index: int = data['response']['items'][0]['text'].index('#')
            date: str = data['response']['items'][0]['text'][:date_ends_index]
            # finds and sorts milongas from polling
            milongas: list = data['response']['items'][0]['attachments'][0]['poll']['answers']  # list of milongas
            milongas.sort(key=lambda _: _['votes'], reverse=True)
            ret = date
            for milonga in milongas:
                assert isinstance(milonga, Dict)
                rate = milonga['rate']
                name = milonga['text']
                votes = milonga['votes']
                ret = ''.join((ret, f'\n{name}\n{rate}% - {votes} чел.'))
            return BotPost(text=ret, photo_urls=[])
        except (KeyError, IndexError) as e:
            raise NonRegularPostResponse(f'Something went wrong while parsing milongas. '
                                         f'Expected structure: [\'response\'][\'items\'][0][\'attachments\'][0]'
                                         f'[\'poll\'][\'answers\'][0...][\'rate\'] | [\' votes\'] | [\'text\']') from e


class OldclothersPrepareStrategy(VKAnswerPrepareBaseStrategy):
    """In case of listening free oldstuff  group"""

    @classmethod
    def prepare_answer(cls, data: Dict) -> BotPost:
        try:
            group_resp: BotPost = cls._presentate_old_or_err(data)
        except (BadRequestException, NonRegularPostResponse) as e:
            warning(e)
            group_resp = BotPost('No result for oldclothers. See terminal log.', photo_urls=[])
        return group_resp

    @classmethod
    def _presentate_old_or_err(cls, data: Dict) -> BotPost:
        """Extracts text from the last post of oldclothers group
        """
        if 'error' in data:
            msg = data['error']['error_msg']
            raise BadRequestException(f'Error while requesting vk api: {msg}')
        try:
            post_photos_urls: List[str] = cls._fetch_photos(data)
            post_text: str = cls._fetch_text(data)
            return BotPost(post_text, post_photos_urls)
        except (KeyError, IndexError) as e:
            raise NonRegularPostResponse(f'Something went wrong while parsing post. '
                                            f'Expected structure: [\'response\'][\'items\'][0][\'text\']') from e

    @classmethod
    def _fetch_photos(cls, data: Dict) -> List[str]:
        """Returns a list of url to attached photos"""
        photo_urls = []
        if 'copy_history' not in data['response']['items'][0]:  # if not a repost
            photos_number = len(data['response']['items'][0]['attachments'][0]['photo']['sizes'])
            [photo_urls.append(data['response']['items'][0]
                               ['attachments'][0]['photo']['sizes'][idx]['url']) for idx in range(photos_number)]
        else:   # if repost - other structure
            photos_number = len(data['response']['items'][0]['copy_history'][0]['attachments'][0]['photo']['sizes'])
            [photo_urls.append(data['response']['items'][0]['copy_history'][0]
                               ['attachments'][0]['photo']['sizes'][idx]['url']) for idx in range(photos_number)]
        return photo_urls

    @classmethod
    def _fetch_text(cls, data: Dict) -> str:
        if 'copy_history' not in data['response']['items'][0]:  # is not repost
            post_text = data['response']['items'][0]['text'] or '_Post text is unavailable_'
        else:   # is a repost
            post_text = data['response']['items'][0]['copy_history'][0]['text'] or '_Post text is unavailable_'
        return post_text


class KvartalPrepareStrategy(VKAnswerPrepareBaseStrategy):

    @classmethod
    def prepare_answer(cls, data: Dict) -> BotPost:
        try:
            group_resp: BotPost = cls._presentate_Kvartal_or_err(data)
        except (BadRequestException, NonRegularPostResponse) as e:
            warning(e)
            group_resp = BotPost('No result for KvartalTango. See terminal log.', photo_urls=[])
        return group_resp
        pass

    @classmethod
    def _presentate_Kvartal_or_err(cls, data):
        if 'error' in data:
            msg = data['error']['error_msg']
            raise BadRequestException(f'Error while requesting vk api: {msg}')
        try:
            # finds date of milonga by # char
            text: int = data['response']['items'][0]['text'] or '_No text available'
            # FIXME: this logic has to be separated to special filtering or fetching strategy while grabbing data
            if all(['Время: ' in text, 'Розенштейна' in text, 'Стоимость' in text]):
                return BotPost(text=text, photo_urls=[])
            else:
                raise NotAppropriateContent(f'The post doesn\'t contain info about kvartal\'s milonga')
        except (KeyError, IndexError) as e:
            raise NonRegularPostResponse(f'Something went wrong while parsing post. '
                                         f'Expected structure: [\'response\'][\'items\'][0] [\'text\']') from e


class VKAnswerPrepareStrategyRegister:
    """Register of various strategies to handle vk answer."""
    _storage = {'milonga': MilongaPrepareStrategy,
                'oldclothers': OldclothersPrepareStrategy,
                'kvartal_tango': KvartalPrepareStrategy
    }

    @classmethod
    def get_strategy_by_group_name(cls, group_name: str) -> type(VKAnswerPrepareBaseStrategy):
        assert cls._storage.keys() == GroupDomainNameAliases._storage.keys()   # FIXME
        return cls._storage[group_name]


class VKHandler:

    def __new__(cls, message: types.Message):
        return cls.handle_vk_by_message(message)

    @classmethod
    def handle_vk_by_message(cls, message: types.Message) -> List[BotPost]:
        ret = []
        group_resp = BotPost(text='No such command', photo_urls=[])

        # prepare keywords
        for key_word in message.text.split(sep=' '):
            alias = key_word[1:]
        # prepare query by keyword and get response
            if alias in GroupDomainNameAliases.as_list():
                data: Dict = VKGroupGrabber.prepare_query_and_grab_data(alias)
                # presentate response
                group_resp: BotPost = VKGroupGrabber.presentate_grabbed_data(alias, data)

            ret.append(group_resp)
        return ret


