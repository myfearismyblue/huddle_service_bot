import logging

from aiogram import Bot, Dispatcher, executor, types

from domain.message_handlers import IParser, AbstractAliasRepo, ISubscriptionRequestFactory, IGrabber, MessageController
from repo import AliasSubscriptionsRepo
from services.grabbers import Grabber
from services.parsers import SplitParser
from services.strategy_registers import QueryStrategyRegister, RepresentStrategyRegister
from services.subscription_request_factories import SubscriptionRequestFactory
from tokens import HUDDLE_SERVICE_BOT_TOKEN as BOT_TOKEN

if __name__ == '__main__':
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    alias_parser: IParser = SplitParser()
    alias_repo: AbstractAliasRepo = AliasSubscriptionsRepo()
    subscription_request_factory: ISubscriptionRequestFactory = SubscriptionRequestFactory(repo=alias_repo)
    grabber: IGrabber = Grabber(QueryStrategyRegister, RepresentStrategyRegister)

    # @dp.inline_handler()
    # async def custom_handler(query):
    #     milonga_query = types.InlineQueryResultArticle(
    #                     id='First id', title="Milongas",
    #                     description="Last posted polling",
    #                     thumb_url='https://sun9-west.userapi.com/sun9-67/s/v1/if2/FlPZoG_0w6Lwt8qg6C68xOSHUG7WFtmtRLUO_QLlWW6XNBLrOT-vYRy_2SUnj5Sk4H2dpUzNTcqSqpYGOflh0i8k.jpg?size=600x600&quality=96&type=album',
    #                     input_message_content=types.InputTextMessageContent(message_text='/milonga'))
    #
    #     oldclothers_query = types.InlineQueryResultArticle(
    #                         id='Second id', title="Отдам даром",
    #                         description="Последний пост группы \"Отдам даром \"",
    #                         thumb_url='https://sun9-west.userapi.com/sun9-13/s/v1/if1/_CFTXZftew3F_o2qb8_6jSxhETtO7-hbBYuWLQMDqpPtL_30nGxRL_MH4uniWsBlI_gulCHZ.jpg?size=1065x1032&quality=96&type=album',
    #                         input_message_content=types.InputTextMessageContent(message_text='/old'))
    #
    #     await bot.answer_inline_query(query.id, [milonga_query, oldclothers_query])
    message_controller = MessageController(grabber=grabber,
                                           parser=alias_parser,
                                           subscription_request_factory=subscription_request_factory).message_controller
    message_controller = dp.message_handler()(message_controller)


    async def on_startup(_):
        logging.warning('Bot is running')

    executor.start_polling(dp, on_startup=on_startup)