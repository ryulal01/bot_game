import random
import time

import emoji
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from app.models import Person, ItemsOnLoc, Item, Inventory, Location, \
	LocationNear, MobLocUser, Mob
from app.utils import info_user, loc_user_info, loc_mana_hp_regenerated_info, \
	loc_mob_info
from config.db import session


class LocationState(StatesGroup):
	waiting_for_select_city_menu_location = State()

	waiting_for_leave_place_selected = State()
	waiting_for_shopping_selected = State()

	waiting_for_select_underground_menu_location = State()
	waiting_for_attack_selected = State()


async def location_start(message: types.Message , state: FSMContext):
	user_in_db = session.query(Person).filter(
		Person.user_id_tg == message.from_user.id).first()
	if not user_in_db:
		await message.answer(
			"Вы в начальном меню!\n"
			"У вас ограниченный доступ\n"
			"выйти из диалога:  /cancel\n"
			"Для полного доступа пройдите регистрацию, нажав:\n /registration",
			reply_markup = types.ReplyKeyboardRemove()
		)
		return
	await state.update_data(given_user_in_db_id = user_in_db.id)
	await message.answer(
		loc_user_info(user_in_db)
	)

	if user_in_db.person_curr_loc.location_type == 'Город':
		user_in_db.hp_current = user_in_db.hp_total
		user_in_db.mana_current = user_in_db.mana_total
		session.commit()
		await message.answer(loc_mana_hp_regenerated_info(user_in_db))

		buttons = [
			types.InlineKeyboardButton(text = f"""Сходить в лавку""",
									   callback_data = f"""shopping"""),
			types.InlineKeyboardButton(
				text = f"""Посмотреть другие локации рядом""",
				callback_data = f"""leave_to"""),
		]

		keyboard = types.InlineKeyboardMarkup(row_width = 1)
		keyboard.add(*buttons)

		await message.answer(f"Что предпочитаете сделать?",
							 reply_markup = keyboard)

		await state.set_state(
			LocationState.waiting_for_select_city_menu_location.state)

	if user_in_db.person_curr_loc.location_type == 'Подземелье':
		buttons = [
			types.InlineKeyboardButton(
				text = f"""Посмотреть информацию о монстре""",
				callback_data = f"""info_mob"""),

		types.InlineKeyboardButton(
				text = f"""Посмотреть другие локации рядом""",
				callback_data = f"""leave_to"""),
			types.InlineKeyboardButton(
				text = f"""Атаковать""",
				callback_data = f"""attack"""),
		]

		keyboard = types.InlineKeyboardMarkup(row_width = 1)
		keyboard.add(*buttons)

		await message.answer(f"Что предпочитаете сделать?",
							 reply_markup = keyboard)

		await state.set_state(
			LocationState.waiting_for_select_underground_menu_location.state)


async def location_menu_underground(call: types.CallbackQuery,
									state: FSMContext):
	previous_data_got = await state.get_data()
	user_in_db_id = previous_data_got.get('given_user_in_db_id')
	user_in_db_obj = session.query(Person).filter(
		Person.id == user_in_db_id).first()

	mob_on_loc_obj = MobLocUser.generate_or_get_mob(user_in_db_obj)
	await state.update_data(given_mob_loc_user_id = mob_on_loc_obj.id)

	if call.data == 'info_mob':
		await call.message.edit_text(
			f'Вы нажали <Посмотреть информацию о монстре> !')
		await call.message.answer(
					loc_mob_info(mob_on_loc_obj))

		await call.message.answer(f"Нажмите\n/menu_location\n"
								  f"чтобы посмотреть меню локации")
		await state.finish()
		return
	if call.data == 'attack':
		await call.message.edit_text(
			f'Вы нажали <Атаковать> !')
		buttons = [
			types.InlineKeyboardButton(text = f"""Атака магией {user_in_db_obj.attack_magic_basic }""",
									   callback_data = f"""attack_magic"""),
			types.InlineKeyboardButton(
				text = f"""Атака силой {user_in_db_obj.attack_force_basic}""",
				callback_data = f"""attack_force"""),
		]

		keyboard = types.InlineKeyboardMarkup(row_width = 1)
		keyboard.add(*buttons)

		await call.message.answer(f"Как атаковать?",
								  reply_markup = keyboard)
		await state.set_state(
			LocationState.waiting_for_attack_selected.state)
	if call.data == 'leave_to':
		await call.message.edit_text(
			f'Вы нажали <Посмотреть другие локации рядом> !')
		near_locations = LocationNear.get_near_locations(
			user_in_db_obj.person_curr_loc.id)

		buttons = [
			types.InlineKeyboardButton(
				text = f"""{loc.loc_second.name} |
				 Идти шагов: {loc.step_to_go}""",
				callback_data = f"""{loc.loc_second.id}|||{loc.step_to_go}""",
			) for loc in near_locations[:5]]

		keyboard = types.InlineKeyboardMarkup(row_width = 1)
		keyboard.add(*buttons)
		keyboard.add(types.InlineKeyboardButton(
			text = f"""Назад""",
			callback_data = f"""back"""))
		await call.message.answer(f"Куда желаете уйти?",
								  reply_markup = keyboard)

		await state.set_state(
			LocationState.waiting_for_leave_place_selected.state)



async def  attack_mob_underground(call: types.CallbackQuery, state: FSMContext):

	previous_data_got = await state.get_data()
	user_in_db_id = previous_data_got.get('given_user_in_db_id')
	mob_loc_user_id = previous_data_got.get('given_mob_loc_user_id')
	user_in_db_obj = session.query(Person).filter(
		Person.id == user_in_db_id).first()

	mob_on_loc_obj = session.query(MobLocUser).filter(
		MobLocUser.id == mob_loc_user_id).first()

	if call.data == 'attack_magic':
		await call.message.edit_text(
			f'Вы нажали <Атака магией> {emoji.emojize(":shooting_star:")}')
		user_attack_magic = user_in_db_obj.attack_magic_basic
		mob_armour_magic = mob_on_loc_obj.mob.armour_magic

		if user_attack_magic > mob_armour_magic:
			await call.message.answer(f'Ваш урон магией '
									  f'{user_attack_magic} '
									  f'больше защиты моба '
									  f'{mob_armour_magic}')
			mob_on_loc_obj.hp_current_mob -= (user_attack_magic-mob_armour_magic)

			if mob_on_loc_obj.hp_current_mob <= 0:
				await call.message.answer(
					f'Здоровье моб погиб')
			await call.message.answer(f"Нажмите\n/menu_location\n"
										  f"чтобы посмотреть меню локации")

			session.query(MobLocUser).filter(
				MobLocUser.id == mob_loc_user_id).delete()
			session.commit()
			await state.finish()
			return


			await call.message.answer(f'Здоровье моба стало: {mob_on_loc_obj.hp_current_mob}')

		else:
			await call.message.answer(
				f'Ваш урон  магией полностью {user_attack_magic} отбила броня моба {mob_armour_magic}')

	if call.data == 'attack_force':
		await call.message.edit_text(
			f'Вы нажали <Атака силой> {emoji.emojize(":boxing_glove:")}!')

		user_attack_force = user_in_db_obj.attack_force_basic
		mob_armour_force = mob_on_loc_obj.mob.armour_force

		if user_attack_force >= mob_armour_force:
			await call.message.answer(f'Ваш урон силой '
									  f'{user_attack_force} '
									  f'больше защиты моба '
									  f'{mob_armour_force}')
			mob_on_loc_obj.hp_current_mob -= (
						user_attack_force - mob_armour_force)

			if mob_on_loc_obj.hp_current_mob <=0:
				await call.message.answer(
					f'Здоровье моб погиб')
			await call.message.answer(f"Нажмите\n/menu_location\n"
										  f"чтобы посмотреть меню локации")
			session.query(MobLocUser).filter(
				MobLocUser.id == mob_loc_user_id).delete()
			session.commit()
			await state.finish()
			return

			await call.message.answer(
				f'Здоровье моба стало: {mob_on_loc_obj.hp_current_mob}')

		else:
			await call.message.answer(
				f'Ваш урон силой полностью {user_attack_force} отбила броня моба {mob_armour_force}')




	mob_attack = mob_on_loc_obj.mob.attack
	if mob_on_loc_obj.mob.attack_type == 'Магическая':
		await call.message.answer(
			f'Моб напал магией')

		user_armour_magic = user_in_db_obj.armour_magic_basic
		if user_armour_magic >= mob_attack:
			await call.message.answer('Ваша броня '
									  f'{user_armour_magic} '
									  ' полностью поглатила урон '
									  f'{mob_attack} '
									  'магией моба')

		else:
			await call.message.answer(f'Урон моба магией '
									  f'{mob_attack} '
									  f'больше вашей защиты '
									  f'{user_armour_magic}')

			user_in_db_obj.hp_current -= (
						mob_attack - user_armour_magic)
			await call.message.answer(
				f'Ваше здоровье стало: {user_in_db_obj.hp_current}')




	elif mob_on_loc_obj.mob.attack_type == 'Силовая':
		await call.message.answer(
			f'Моб напал силой')

		user_armour_force = user_in_db_obj.armour_force_basic

		if user_armour_force >= mob_attack:
			await call.message.answer('Ваша броня '
									  f'{user_armour_force} '
									  ' полностью поглатила урон '
									  f'{mob_attack} '
									  'силой моба ')

		else:
			await call.message.answer(f'Урон моба силой '
									  f'{mob_attack} '
									  f'больше вашей защиты '
									  f'{user_armour_force}')

			user_in_db_obj.hp_current -= (
					mob_attack - user_armour_force)
			await call.message.answer(
				f'Ваше здоровье стало: {user_in_db_obj.hp_current}')

	session.commit()
	await call.message.answer(f"Нажмите\n/menu_location\n"
							  f"чтобы посмотреть меню локации")
	await state.finish()

async def location_menu_city(call: types.CallbackQuery, state: FSMContext):
	previous_data_got = await state.get_data()
	user_in_db_id = previous_data_got.get('given_user_in_db_id')

	user_in_db_obj = session.query(Person).filter(
		Person.id == user_in_db_id).first()

	items_in_city = session.query(ItemsOnLoc).filter(
		ItemsOnLoc.loc_rel == user_in_db_obj.person_curr_loc.id,
		ItemsOnLoc.quantity >= 1).all()

	if call.data == 'shopping':

		if not items_in_city:
			await call.message.answer(
				'В магазине закончились товары,'
				'посетите другой город в надежде что-либо купить')
			await state.finish()
			return
		await call.message.edit_text('Вы выбрали сходить в лавку!')
		buttons = [
			types.InlineKeyboardButton(
				text = f"""{row.item.name} |
				 Цена: {row.item.cost_to_sale}
				 \nШтук в наличии {row.quantity}""",
				callback_data = f"""item|||{row.item.id}""",
			) for row in items_in_city[:5]]

		keyboard = types.InlineKeyboardMarkup(row_width = 1)
		keyboard.add(*buttons)
		keyboard.add(types.InlineKeyboardButton(
			text = f"""Назад""",
			callback_data = f"""back"""))

		await call.message.answer(f"Нажмите на предмет чтобы купить",
								  reply_markup = keyboard)

		await state.set_state(LocationState.waiting_for_shopping_selected.state)

	if call.data == 'leave_to':
		await call.message.edit_text(
			f'Вы нажали <Посмотреть другие локации рядом> !')
		near_locations = LocationNear.get_near_locations(
			user_in_db_obj.person_curr_loc.id)

		buttons = [
			types.InlineKeyboardButton(
				text = f"""{loc.loc_second.name} |
				 Идти шагов: {loc.step_to_go}""",
				callback_data = f"""{loc.loc_second.id}|||{loc.step_to_go}""",
			) for loc in near_locations[:5]]

		keyboard = types.InlineKeyboardMarkup(row_width = 1)
		keyboard.add(*buttons)
		keyboard.add(types.InlineKeyboardButton(
			text = f"""Назад""",
			callback_data = f"""back"""))
		await call.message.answer(f"Куда желаете уйти?",
								  reply_markup = keyboard)

		await state.set_state(
			LocationState.waiting_for_leave_place_selected.state)


async def location_go_away(call: types.CallbackQuery, state: FSMContext):
	previous_data_got = await state.get_data()
	user_in_db_id = previous_data_got.get('given_user_in_db_id')

	user_in_db_obj = session.query(Person).filter(
		Person.id == user_in_db_id).first()

	if call.data == 'back':
		await call.message.edit_text(
			f'Вы нажали <Назад> !')

		await call.message.answer(f"Нажмите\n/menu_location\n"
								  f"чтобы посмотреть меню локации")
		await state.finish()
		return

	loc_id_to_go, step_to_go = call.data.split("|||")
	loc_id_to_go = int(loc_id_to_go)
	step_to_go = int(step_to_go)

	loc_obj = session.query(Location).filter(
		Location.id == loc_id_to_go).first()
	await call.message.edit_text(
		f'Вы выбрали переход в <{loc_obj.name}> !')

	await call.message.answer(
		f'Идем в выбранную локацию, шагов: <{step_to_go}> !')
	for i in range(step_to_go):
		i += 1
		time.sleep(1)
		await call.message.answer(
			f'Идем {emoji.emojize(":person_running: ") * i}')
	await call.message.answer(
		f'Теперь пришли в {loc_obj.name}')

	user_in_db_obj.curr_loc = loc_id_to_go
	session.commit()

	await call.message.answer(info_user(user_in_db_obj))
	await call.message.answer(f"Нажмите\n/menu_location\n"
							  f"чтобы посмотреть меню локации")
	await state.finish()


async def location_shopping(call: types.CallbackQuery, state: FSMContext):
	previous_data_got = await state.get_data()
	given_user_in_db_id = previous_data_got.get('given_user_in_db_id')
	user_obj = session.query(Person).filter(
		Person.id == given_user_in_db_id).first()

	if not call.data == 'back':
		item_to_buy_id = int(call.data.split("|||")[-1])

		item_to_buy_obj = session.query(Item).filter(
			Item.id == item_to_buy_id).first()

		if user_obj.money >= item_to_buy_obj.cost_to_sale:
			user_obj.money -= item_to_buy_obj.cost_to_sale

			inventory_check_item_user = session.query(
				Inventory).filter(
				Inventory.user_rel == user_obj.id,
				Inventory.item_rel == item_to_buy_obj.id).first()

			if inventory_check_item_user:
				inventory_check_item_user.quantity += 1
			else:
				new_obj = Inventory(user_rel = user_obj.id,
									item_rel = item_to_buy_obj.id,
									quantity = 1,
									usage = 1,
									)
				session.add(new_obj)
			try:
				item_on_loc = session.query(
					ItemsOnLoc).filter(
					ItemsOnLoc.item_rel == item_to_buy_obj.id).first()
				item_on_loc.quantity -= 1
				session.commit()
			except Exception as e:
				print('Ошибка при загрузке покупки в базу')
				print(e)
				session.rollback()
				await call.message.answer(
					'В магазине отключили свет за неоплату, зайдите позже')
				await state.finish()
				return
			else:
				await call.message.edit_text(
					f'Вы успешно купили {item_to_buy_obj.name}!\nПриходите еще!')
				await call.message.answer(info_user(user_obj))

	if call.data == 'back':
		await call.message.edit_text(
			f'Вы нажали <Назад> !')
	buttons = [
		types.InlineKeyboardButton(text = f"""Остаться в лавке""",
								   callback_data = f"""shopping"""),
		types.InlineKeyboardButton(
			text = f"""Посмотреть другие локации рядом""",
			callback_data = f"""leave_to"""),
	]

	keyboard = types.InlineKeyboardMarkup(row_width = 1)
	keyboard.add(*buttons)

	await call.message.answer(f"Что предпочитаете сделать?",
							  reply_markup = keyboard)

	await state.set_state(
		LocationState.waiting_for_select_city_menu_location.state)


def register_handlers_location(dp: Dispatcher):
	dp.register_message_handler(location_start, commands = "menu_location",
								state = "*")

	dp.register_callback_query_handler(location_menu_city,
									   state = LocationState.waiting_for_select_city_menu_location)

	dp.register_callback_query_handler(location_shopping,
									   state = LocationState.waiting_for_shopping_selected)
	dp.register_callback_query_handler(location_go_away,
									   state = LocationState.waiting_for_leave_place_selected)

	dp.register_callback_query_handler(location_menu_underground,
									   state = LocationState.waiting_for_select_underground_menu_location)
	dp.register_callback_query_handler(attack_mob_underground,
									   state = LocationState.waiting_for_attack_selected)