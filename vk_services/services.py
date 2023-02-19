import json
from logging import warning
from typing import Dict

import requests as requests

from aiogram import types

from vk_services.vk_container import domain, access_token, user_id
from vk_services.vk_exceptions import BadRequestException, NonRegularMilongaResponse


def _fetch_pretty_json(vk_query, indent=4):
    """Fetches response and gets text as pretty json from it"""
    response = requests.get(vk_query)
    data = response.text
    json_string = json.dumps(json.loads(data), indent=indent, ensure_ascii=False).encode('utf8')
    return json_string


def _fetch_json(vk_query):
    response = requests.get(vk_query)
    return response.json()

def _build_vk_query(domain_id: str):
    vk_query = f"{domain}/wall.get?access_token={access_token}&user_id={user_id}&" \
               f"domain={domain_id}&count={1}&v=5.84"
    return vk_query


def _presentate_milongas_or_err(data: Dict):
    """Extract polling answers from post attachment, sorts with milonga rate and returns formatted string.
    If error occurred while responding or can't find milongas inside valid response raises corresponding exception
    """
    if 'error' in data:
        msg = data['error']['error_msg']
        raise BadRequestException(f'Error while requesting vk api: {msg}')
    try:
        milongas: list = data['response']['items'][0]['attachments'][0]['poll']['answers']  # list of milongas
        milongas.sort(key=lambda _: _['votes'], reverse=True)
        ret = ''
        for milonga in milongas:
            assert isinstance(milonga, Dict)
            rate = milonga['rate']
            name = milonga['text']
            votes = milonga['votes']
            ret = ''.join((ret, f'\n{name}\n{rate}% - {votes} чел.'))
        return ret
    except (KeyError, IndexError) as e:
        raise NonRegularMilongaResponse(f'Something went wrong while parsing milongas. '
                                        f'Expected structure: [\'response\'][\'items\'][0][\'attachments\'][0]'
                                        f'[\'poll\'][\'answers\'][0...][\'rate\'] | [\' votes\'] | [\'text\']') from e


def handle_vk_by_message(message: types.Message):
    if 'milonga' in message.text:
        vk_query = _build_vk_query('milonga')
        data = _fetch_json(vk_query)
        try:
            ret: str = _presentate_milongas_or_err(data)
            return ret

        except (BadRequestException, NonRegularMilongaResponse) as e:
            warning(e)
            return 'No result. See terminal log.'

