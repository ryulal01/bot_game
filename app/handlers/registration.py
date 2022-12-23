import re
import emoji
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import message
from sqlalchemy.exc import IntegrityError

from app.models import Person
from app.utils import RACES, info_user
from config.db import session


class RegistrationState(StatesGroup):
	waiting_for_nickname = State()
	waiting_for_race = State()


async def registration_start(message: types.Message, state: FSMContext):
	user_in_db = session.query(Person).filter(
		Person.user_id_tg == message.from_user.id).first()
	if user_in_db:
		await message.answer(
			f"Вы уже регистрировались прежде\n")
		await message.answer(info_user(user_in_db)
		)
		return
	await state.update_data(given_user_tg_id = message.from_user.id)
	await message.answer("Введите свой желаемый никнейм:")
	await state.set_state(RegistrationState.waiting_for_nickname.state)


async def nickname_given(message: types.Message, state: FSMContext):
	if not re.match("^[a-zA-Z]+$", message.text):
		await message.answer(
			"Пожалуйста, введите латинскими буквами ваш будущий никнейм")
		return

	await state.update_data(given_nickname = message.text.capitalize())

	buttons = [
		types.InlineKeyboardButton(text = f"""{row.get('race_name')}""",
								   callback_data = f"""race_city|||{row.get('start_city_id')}""",
								   ) for row in RACES.values()]

	keyboard = types.InlineKeyboardMarkup(row_width = 3)
	keyboard.add(*buttons)

	await message.answer(f"Теперь выберите расу:",
						 reply_markup = keyboard)

	await state.set_state(RegistrationState.waiting_for_race.state)


async def race_given(call: types.CallbackQuery, state: FSMContext):
	race_selected = int(call.data.split("|||")[-1])

	race_name_selected = RACES.get(race_selected).get('race_name')

	await call.message.edit_text(
		f"""Вы выбрали расу: {RACES.get(race_selected).get('race_name')}""")
	attack_force_basic_selected = RACES.get(race_selected).get(
		'attack_force_basic')
	armour_force_basic_selected = RACES.get(race_selected).get(
		'armour_force_basic')
	hp_total_selected = RACES.get(race_selected).get('hp_total')
	attack_magic_basic_selected = RACES.get(race_selected).get(
		'attack_magic_basic')
	armour_magic_basic_selected = RACES.get(race_selected).get(
		'armour_magic_basic')
	mana_total_selected = RACES.get(race_selected).get('mana_total')
	money_selected = RACES.get(race_selected).get('money')
	start_city_id_selected = RACES.get(race_selected).get('start_city_id')

	previous_data_got = await state.get_data()
	given_nickname = previous_data_got.get('given_nickname')
	given_user_tg_id = previous_data_got.get('given_user_tg_id')

	person_obj = Person(
		user_id_tg = given_user_tg_id,
		nick_name = given_nickname,
		race_selected = race_name_selected,
		attack_force_basic = attack_force_basic_selected,
		attack_magic_basic = attack_magic_basic_selected,
		armour_force_basic = armour_force_basic_selected,
		armour_magic_basic = armour_magic_basic_selected,
		base_city=start_city_id_selected,
		curr_loc = start_city_id_selected,
		money = money_selected,
		mana_total = mana_total_selected,
		mana_current = mana_total_selected,
		hp_total = hp_total_selected,
		hp_current = hp_total_selected,
		level = 1,
		experience_on_level = 1,

	)
	try:
		session.add(person_obj)
		session.commit()
	except IntegrityError as e:
		print(e)
		session.rollback()
		await message.answer(
			f"Вы уже регистрировались прежде\n")
		await state.finish()
	except Exception as e:
		print(e)
		session.rollback()
		await message.answer(
			f"Какой то сбой, попробуйте позже\n")
		await state.finish()
	else:
		await call.message.answer(info_user(person_obj))
		await call.message.answer(
			f"Нажмите /start, чтобы посмотреть доступные вам команды")
		await state.finish()


def register_handlers_registration(dp: Dispatcher):
	dp.register_message_handler(registration_start, commands = "registration",
								state = "*")
	dp.register_message_handler(nickname_given,
								state = RegistrationState.waiting_for_nickname)
	dp.register_callback_query_handler(race_given,
									   state = RegistrationState.waiting_for_race)
