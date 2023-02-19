# initial app
import logging

import sys
sys.path.append('../venv/lib/python3.8/site-packages')

from aiogram import Bot, Dispatcher, executor, types

from tokens import HUDDLE_SERVICE_BOT_TOKEN as BOT_TOKEN

if __name__ == '__main__':
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    @dp.message_handler(commands=['start', 'help'])
    async def start_handler(message: types.Message):
        await message.answer(f"Hello, {message.from_user.id}")

    @dp.message_handler()
    async def echo_handler(message: types.Message):
        await message.answer(f"From message handler: {message.text}")

    @dp.inline_handler()
    async def custom_handler(query):
        text = 'Inline greetings'
        r_sum = types.InlineQueryResultArticle(
            id='First id', title="Hint",
            description="Description",
            input_message_content=types.InputTextMessageContent(message_text=text))
        await bot.answer_inline_query(query.id, [r_sum])

    async def on_startup(_):
        logging.warning('Bot is running')

    executor.start_polling(dp, on_startup=on_startup)
