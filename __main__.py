import logging

from aiogram import Bot, Dispatcher, executor

from domain.message_handlers import IParser, AbstractAliasRepo, ISubscriptionRequestFactory, IGrabber, MessageControllerFactory
from repo import AliasSubscriptionsRepo
from services.grabbers import Grabber
from services.parsers import SplitParser, ListenParser
from services.strategy_registers import QueryStrategyRegister, RepresentStrategyRegister
from services.subscription_request_factories import SubscriptionRequestFactory
from tokens import HUDDLE_SERVICE_BOT_TOKEN as BOT_TOKEN

if __name__ == '__main__':
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    alias_parser: IParser = ListenParser()
    alias_repo: AbstractAliasRepo = AliasSubscriptionsRepo()
    subscription_request_factory: ISubscriptionRequestFactory = SubscriptionRequestFactory(repo=alias_repo)
    grabber: IGrabber = Grabber(QueryStrategyRegister, RepresentStrategyRegister)

    message_controller = MessageControllerFactory(grabber=grabber,
                                                  parser=alias_parser,
                                                  subscription_request_factory=subscription_request_factory)
    message_controller = dp.message_handler(commands=['listen'])(message_controller)


    async def on_startup(_):
        logging.warning('Bot is running')

    executor.start_polling(dp, on_startup=on_startup)