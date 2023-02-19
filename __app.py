# initial app
import logging

from aiogram import Bot, Dispatcher, executor, types

from tokens import HUDDLE_SERVICE_BOT_TOKEN as BOT_TOKEN

if __name__ == '__main__':
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    @dp.message_handler(commands=['start', 'help'])
    async def start_handler(message: types.Message):
        await message.answer(f"Hello, {message.from_user.id}")

    async def on_startup(_):
        logging.warning('Bot is running')

    executor.start_polling(dp, on_startup=on_startup)
