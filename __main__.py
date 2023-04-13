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

    command = 'listen'
    listen_message_controller = MessageControllerFactory(
        grabber=Grabber(QueryStrategyRegister, RepresentStrategyRegister),
        parser=ListenParser(),
        subscription_request_factory=SubscriptionRequestFactory(repo=AliasSubscriptionsRepo()),
        command=command)

    listen_message_controller = dp.message_handler(commands=[command])(listen_message_controller)

    command = ''
    message_controller = MessageControllerFactory(
        grabber=Grabber(QueryStrategyRegister, RepresentStrategyRegister),
        parser=SplitParser(),
        subscription_request_factory=SubscriptionRequestFactory(repo=AliasSubscriptionsRepo()),
        command=command)

    message_controller = dp.message_handler()(message_controller)


    async def on_startup(_):
        logging.warning('Bot is running')

    executor.start_polling(dp, on_startup=on_startup)