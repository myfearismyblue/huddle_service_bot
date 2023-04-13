from logging import warning
from typing import Protocol, List, Dict

from domain.message_handlers import JSONType, BotPost, SubscriptionRequest
from services.exceptions import VKNonRegularPostResponse, VKBadRequestException, NotAppropriateContent


class RepresentStrategy(Protocol):
    """Abstract protocol to handle concrete strategies for representation of services' api answers"""

    def represent(self, subscription_request: SubscriptionRequest, data: JSONType) -> BotPost:
        ...


class MilongaRepresentStrategy:
    """In case of listening daily milongas vk.com group"""

    @classmethod
    def represent(cls, subscription_request: SubscriptionRequest, data: JSONType) -> BotPost:
        try:
            group_resp: BotPost = cls._presentate_milongas_or_err(data)
        except (VKBadRequestException, VKNonRegularPostResponse) as e:
            warning(e)
            group_resp = BotPost(text='No result for milongas. See terminal log.', photo_urls=[])
        return group_resp

    @classmethod
    def _presentate_milongas_or_err(cls, data: JSONType) -> BotPost:
        """Extract polling answers from post attachment, sorts with milonga rate and returns formatted string.
        If error occurred while responding or can't find milongas inside valid response raises corresponding exception
        """
        if 'error' in data:
            msg = data['error']['error_msg']
            raise VKBadRequestException(f'Error while requesting vk api: {msg}')
        try:
            # finds date of milonga by # char
            date_ends_index: int = data['response']['items'][0]['text'].index('#')
            date: str = data['response']['items'][0]['text'][:date_ends_index]
            # finds and sorts milongas from polling
            milongas: JSONType = data['response']['items'][0]['attachments'][0]['poll']['answers']  # list of milongas
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
            raise VKNonRegularPostResponse(f'Something went wrong while parsing milongas. '
                                           f'Expected structure: [\'response\'][\'items\'][0][\'attachments\'][0]'
                                           f'[\'poll\'][\'answers\'][0...][\'rate\'] | [\' votes\'] | [\'text\']') from e


class OldclothersRepresentStrategy:
    @classmethod
    def represent(cls, subscription_request: SubscriptionRequest, data: Dict) -> BotPost:
        try:
            group_resp: BotPost = cls._represent_old_or_err(data)
        except (VKBadRequestException, VKNonRegularPostResponse) as e:
            warning(e)
            group_resp = BotPost('No result for oldclothers. See terminal log.', photo_urls=[])
        return group_resp

    @classmethod
    def _represent_old_or_err(cls, data: JSONType) -> BotPost:
        """Extracts text from the last post of oldclothers group
        """
        if 'error' in data:
            msg = data['error']['error_msg']
            raise VKBadRequestException(f'Error while requesting vk api: {msg}')
        try:
            post_photos_urls: List[str] = cls._fetch_photos(data)
            post_text: str = cls._fetch_text(data)
            return BotPost(post_text, post_photos_urls)
        except (KeyError, IndexError) as e:
            raise VKNonRegularPostResponse(f'Something went wrong while parsing post. '
                                           f'Expected structure: [\'response\'][\'items\'][0][\'text\']') from e

    @classmethod
    def _fetch_photos(cls, data: JSONType) -> List[str]:
        """Returns a list of url of attached photos"""
        photo_urls = []
        if 'copy_history' not in data['response']['items'][0]:  # if not a repost
            photos_number = len(data['response']['items'][0]['attachments'])
            [photo_urls.append(data['response']['items'][0]
                               ['attachments'][idx]['photo']['sizes'][-1]['url']) for idx in range(photos_number)]
        else:  # if repost - other structure
            photos_number = len(data['response']['items'][0]['copy_history'][0]['attachments'])
            [photo_urls.append(data['response']['items'][0]['copy_history'][0]
                               ['attachments'][idx]['photo']['sizes'][-1]['url']) for idx in range(photos_number)]
        return photo_urls

    @classmethod
    def _fetch_text(cls, data: JSONType) -> str:
        if 'copy_history' not in data['response']['items'][0]:  # is not repost
            post_text = data['response']['items'][0]['text'] or '_Post text is unavailable_'
        else:  # is a repost
            post_text = data['response']['items'][0]['copy_history'][0]['text'] or '_Post text is unavailable_'
        return post_text


class KvartalRepresentStrategy:

    @classmethod
    def represent(cls, subscription_request: SubscriptionRequest, data: Dict) -> BotPost:
        try:
            group_resp: BotPost = cls._presentate_Kvartal_or_err(data)
        except (VKBadRequestException, VKNonRegularPostResponse) as e:
            warning(e)
            group_resp = BotPost('No result for KvartalTango. See terminal log.', photo_urls=[])
        return group_resp
        pass

    @classmethod
    def _presentate_Kvartal_or_err(cls, data: JSONType) -> BotPost:
        if 'error' in data:
            msg = data['error']['error_msg']
            raise VKBadRequestException(f'Error while requesting vk api: {msg}')
        try:
            # finds date of milonga by # char
            text: str = data['response']['items'][0]['text'] or '_No text available'
            # FIXME: this logic has to be separated to special filtering or fetching strategy while grabbing data
            if all(['Время: ' in text, 'Розенштейна' in text, 'Стоимость' in text]):
                return BotPost(text=text, photo_urls=[])
            else:
                raise NotAppropriateContent(f'The post doesn\'t contain info about kvartal\'s milonga')
        except (KeyError, IndexError) as e:
            raise VKNonRegularPostResponse(f'Something went wrong while parsing post. '
                                         f'Expected structure: [\'response\'][\'items\'][0] [\'text\']') from e