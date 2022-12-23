from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from app.models import Person
from app.utils import info_user, loc_user_info
from config.db import session


async def cmd_start(message: types.Message, state: FSMContext):
	await state.finish()

	user_in_db = session.query(Person).filter(
		Person.user_id_tg == message.from_user.id).first()
	if not user_in_db:
		await message.answer(
			"Вы в начальном меню!\n"
			"У вас ограниченный доступ\n"
			"Вы можете:\n"
			"\n"


			"выйти из диалога:  /cancel\n"
			"Для полного доступа пройдите регистрацию, нажав:\n /registration",
			reply_markup = types.ReplyKeyboardRemove()
		)
		return
	await message.answer(
		f"{loc_user_info(user_in_db)}"
		"\n""\n"
		f"""нажмите /menu_location\n"""
		f"""Чтобы посмотреть свои возможности\n"""
		"выйти из диалога: /cancel\n",
		reply_markup = types.ReplyKeyboardRemove()
	)


async def cmd_cancel(message: types.Message, state: FSMContext):
	await state.finish()
	await message.answer("Вы окончили предыдущий диалог",
						 reply_markup = types.ReplyKeyboardRemove())
async def cmd_my_info(message: types.Message):
	user_in_db = session.query(Person).filter(
		Person.user_id_tg == message.from_user.id).first()
	if not user_in_db:
		await message.answer(
			"Мы пока о вас ничего не знаем!\n"
			"Зарегистрируйтесь, нажав:\n /registration",
			reply_markup = types.ReplyKeyboardRemove()
		)

	await message.answer(info_user(user_in_db))


def register_handlers_common(dp: Dispatcher):
	dp.register_message_handler(cmd_start, commands = "start", state = "*")
	dp.register_message_handler(cmd_cancel, commands = "cancel", state = "*")
	dp.register_message_handler(cmd_my_info, commands = "my_info", state = "*")
