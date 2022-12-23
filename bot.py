import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.handlers.common import register_handlers_common
from app.handlers.location_city import register_handlers_location
from app.handlers.registration import register_handlers_registration
from app.models import init_db
from config.tokens import TOKEN_TG


async def set_commands(bot: Bot):
	commands = [
		BotCommand(command = "/registration",
				   description = "Пройти регистрацию"),
		BotCommand(command = "/cancel",
				   description = "Отменить текущее действие"),
		BotCommand(command = "/my_info",
				   description = "Информация обо мне в системе"),
		BotCommand(command = "/menu_location",
				   description = "Информация о возможности локации"),
	]
	await bot.set_my_commands(commands)



async def main():
	bot = Bot(token = TOKEN_TG)
	dp = Dispatcher(bot, storage = MemoryStorage())



	register_handlers_common(dp)
	register_handlers_registration(dp)
	register_handlers_location(dp)

	await set_commands(bot)

	await dp.start_polling()

if __name__ == '__main__':
	init_db()
	asyncio.run(main())
