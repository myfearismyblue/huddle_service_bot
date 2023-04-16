import logging
from typing import Type

from aiogram import Bot, Dispatcher, executor

from domain import MessageControllerFactory, AbstractUoW, AbstractAliasRepo
from repo import AliasSubscriptionsRepo, SubscriptionRepo
from services.grabbers import Grabber, AllSubscriptionsDummyGrabber
from services.parsers import SplitParser, ListenParser
from services.strategy_registers import QueryStrategyRegister, RepresentStrategyRegister
from services.subscription_request_factories import SubscriptionRequestFactory, AllSubscriptionRequestFactory
from services.unit_of_work import DjangoUoW
from tokens import HUDDLE_SERVICE_BOT_TOKEN as BOT_TOKEN

if __name__ == '__main__':
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    alias_repo: Type[AbstractAliasRepo] = AliasSubscriptionsRepo
    uow: AbstractUoW = DjangoUoW(AliasSubscriptionsRepo)

    command = 'listen'
    listen_message_controller = MessageControllerFactory(
        grabber=Grabber(QueryStrategyRegister, RepresentStrategyRegister),
        parser=ListenParser(),
        subscription_request_factory=SubscriptionRequestFactory(uow=uow),
        command=command)
    listen_message_controller = dp.message_handler(commands=[command])(listen_message_controller)

    command = 'all'
    all_uow: AbstractUoW = DjangoUoW(SubscriptionRepo)
    all_subscriptions_message_controller = MessageControllerFactory(
        grabber=AllSubscriptionsDummyGrabber(),
        parser=SplitParser(),
        subscription_request_factory=AllSubscriptionRequestFactory(uow=all_uow),
        command=command)
    all_subscriptions_message_controller = dp.message_handler(commands=[command])(all_subscriptions_message_controller)

    command = ''
    message_controller = MessageControllerFactory(
        grabber=Grabber(QueryStrategyRegister, RepresentStrategyRegister),
        parser=SplitParser(),
        subscription_request_factory=SubscriptionRequestFactory(uow=uow),
        command=command)
    message_controller = dp.message_handler()(message_controller)


    async def on_startup(_):
        logging.warning('Bot is running')


    executor.start_polling(dp, on_startup=on_startup)
