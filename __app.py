# initial app
import logging

import sys
sys.path.append('../venv/lib/python3.8/site-packages')

from vk_services.services import GroupDomainNameAliases, VKHandler, VKGroupGrabber

from aiogram import Bot, Dispatcher, executor, types

from tokens import HUDDLE_SERVICE_BOT_TOKEN as BOT_TOKEN

if __name__ == '__main__':
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    @dp.message_handler(commands=GroupDomainNameAliases.as_list())
    async def vk_handler(message: types.Message):
        resp = VKHandler(message)
        await message.answer(f"{resp}")

    @dp.message_handler()
    async def echo_handler(message: types.Message):
        await message.answer(f"Unsupportable: {message.text}")

    @dp.inline_handler()
    async def custom_handler(query):
        milonga_query = types.InlineQueryResultArticle(
                        id='First id', title="Milongas",
                        description="Last posted polling",
                        thumb_url='https://sun9-west.userapi.com/sun9-67/s/v1/if2/FlPZoG_0w6Lwt8qg6C68xOSHUG7WFtmtRLUO_QLlWW6XNBLrOT-vYRy_2SUnj5Sk4H2dpUzNTcqSqpYGOflh0i8k.jpg?size=600x600&quality=96&type=album',
                        input_message_content=types.InputTextMessageContent(message_text='/milonga'))

        oldclothers_query = types.InlineQueryResultArticle(
                            id='Second id', title="Отдам даром",
                            description="Последний пост группы \"Отдам даром \"",
                            thumb_url='https://sun9-west.userapi.com/sun9-13/s/v1/if1/_CFTXZftew3F_o2qb8_6jSxhETtO7-hbBYuWLQMDqpPtL_30nGxRL_MH4uniWsBlI_gulCHZ.jpg?size=1065x1032&quality=96&type=album',
                            input_message_content=types.InputTextMessageContent(message_text='/old'))

        await bot.answer_inline_query(query.id, [milonga_query, oldclothers_query])

    async def on_startup(_):
        logging.warning('Bot is running')

    executor.start_polling(dp, on_startup=on_startup)
