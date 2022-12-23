import emoji




RACES = {
	1:
		{
			'race_name': 'Сильные',

			'attack_force_basic': 5,
			'armour_force_basic': 5,
			'hp_total': 5,

			'attack_magic_basic': 1,
			'armour_magic_basic': 1,
			'mana_total': 1,

			'money': 10,

			'start_city_id': 1,
			'race_emoji': 'superhero',
			'arm_emoji': 'crossed_swords'
		},
	3:
		{
			'race_name': 'Магические',
			'attack_force_basic': 1,
			'armour_force_basic': 1,
			'hp_total': 5,

			'attack_magic_basic': 5,
			'armour_magic_basic': 5,
			'mana_total': 5,

			'money': 10,

			'start_city_id': 3,
			'race_emoji': 'mage',
			'arm_emoji': 'magic_wand'
		},
	5:
		{
			'race_name': 'Балансированные',
			'attack_force_basic': 3,
			'armour_force_basic': 3,
			'hp_total': 5,

			'attack_magic_basic': 3,
			'armour_magic_basic': 3,
			'mana_total': 3,

			'money': 10,

			'start_city_id': 5,
			'race_emoji': 'balance_scale',
			'arm_emoji': 'turtle'
		},

}

LOCATIONS = [
	{
		'loc_id': 1,
		'name': 'Город сильных',
		'coord_x': 1,
		'coord_y': 1,
		'location_type': 'Город',

	},
	{
		'loc_id': 2,
		'name': 'Подземелье в горах',
		'coord_x': 10,
		'coord_y': 3,
		'location_type': 'Подземелье',
	},
	{
		'loc_id': 3,
		'name': 'Город Магических',
		'coord_x': 12,
		'coord_y': 18,
		'location_type': 'Город',

	},
	{
		'loc_id': 4,
		'name': 'Подземелье в равнинах',
		'coord_x': 6,
		'coord_y': 17,
		'location_type': 'Подземелье',

	},

	{
		'loc_id': 5,
		'name': 'Город Балансированных',
		'coord_x': 18,
		'coord_y': 15,
		'location_type': 'Город',

	},
]


def info_user(user_obj):
	message = (f"Вы зарегистрировались под ником: {user_obj.nick_name}!\n"
			   f"Ваша раса: "
			   f"""{user_obj.race_selected} """
			   f"""{emoji.emojize(
				   f":{RACES.get(user_obj.base_city).get('race_emoji')}:")}\n"""
			   f"Пример оружия: "
			   f"""{emoji.emojize(
				   f":{RACES.get(user_obj.base_city).get('arm_emoji')}:")}\n"""
			   f"Базовая атака силой: {user_obj.attack_force_basic}\n"
			   f"Базовая защита силой: {user_obj.armour_force_basic}\n"
			   f"ХП: {user_obj.hp_current} из {user_obj.hp_total}\n"
			   f"Базовая атака магией: {user_obj.attack_magic_basic}\n"
			   f"Базовая защита магией: {user_obj.armour_magic_basic}\n"
			   f"МАНА: {user_obj.mana_current} из {user_obj.mana_total}\n"
			   f"Всего денег: {user_obj.money}\n"
			   f"Стартовый город: {user_obj.person_base_city.name}\n"
			   f"Местоположение: {user_obj.person_curr_loc.name}\n"
			   f"Х координаты: {user_obj.person_curr_loc.coord_x}\n"
			   f"Y координаты: {user_obj.person_curr_loc.coord_y}\n")
	return message


# Column(Enum('Оружие', 'Броня', 'Шлем', 'Сапоги', 'Наручи', 'Зелье'))
ITEMS = [
	{
		'id': 1,
		'name': 'Базовое оружие',
		'cost': 1,
		'cost_to_sale': 1,
		'item_type': 'Оружие',
		'hp_add': 2,
		'mana_add': 2,
		'attack_force_add': 2,
		'attack_magic_add': 2,
		'armour_force_add': 2,
		'armour_magic_add': 2,
		'req_level': 1,
	}, {
		'id': 2,
		'name': 'Базовая Броня',
		'cost': 1,
		'cost_to_sale': 1,
		'item_type': 'Броня',
		'hp_add': 2,
		'mana_add': 2,
		'attack_force_add': 2,
		'attack_magic_add': 2,
		'armour_force_add': 2,
		'armour_magic_add': 2,
		'req_level': 1,
	}, {
		'id': 3,
		'name': 'Базовый Шлем',
		'cost': 1,
		'cost_to_sale': 1,
		'item_type': 'Шлем',
		'hp_add': 2,
		'mana_add': 2,
		'attack_force_add': 2,
		'attack_magic_add': 2,
		'armour_force_add': 2,
		'armour_magic_add': 2,
		'req_level': 1,
	}, {
		'id': 4,
		'name': 'Базовые Сапоги',
		'cost': 1,
		'cost_to_sale': 1,
		'item_type': 'Сапоги',
		'hp_add': 2,
		'mana_add': 2,
		'attack_force_add': 2,
		'attack_magic_add': 2,
		'armour_force_add': 2,
		'armour_magic_add': 2,
		'req_level': 1,
	}, {
		'id': 5,
		'name': 'Базовые Наручи',
		'cost': 1,
		'cost_to_sale': 1,
		'item_type': 'Наручи',
		'hp_add': 2,
		'mana_add': 2,
		'attack_force_add': 2,
		'attack_magic_add': 2,
		'armour_force_add': 2,
		'armour_magic_add': 2,
		'req_level': 1,
	}, {
		'id': 6,
		'name': 'Базовое Зелье',
		'cost': 1,
		'cost_to_sale': 1,
		'item_type': 'Зелье',
		'hp_add': 2,
		'mana_add': 2,
		'attack_force_add': 2,
		'attack_magic_add': 2,
		'armour_force_add': 2,
		'armour_magic_add': 2,
		'req_level': 1,
	},
]

MOBS = [
	{
		'id': 1,
		'hp_total': 3,
		'req_level': 1,
		'attack_type': 'Магическая',
		'attack': 1,
		'armour_force': 1,
		'armour_magic': 1,
	},
	{
		'id': 2,
		'hp_total': 3,
		'req_level': 1,
		'attack_type': 'Силовая',
		'attack': 1,
		'armour_force': 1,
		'armour_magic': 1,
	},
]


def loc_user_info(user_obj):
	return ("Ваш герой находится в локации:\n"
			f"{user_obj.person_curr_loc.name}\n"
			f"По координате Х: {user_obj.person_curr_loc.coord_x}\n"
			f"По координате Y: {user_obj.person_curr_loc.coord_y}\n")


def loc_mob_info(mob_loc_obj):
	return (
		f"""Здоровье моба: {mob_loc_obj.hp_current_mob} из {mob_loc_obj.mob.hp_total}"""
			"""\n"""
		f"""Уровень: {mob_loc_obj.mob.req_level}"""
			"""\n"""
		f"""Тип атаки: {mob_loc_obj.mob.attack_type}"""
			"""\n"""
		f"""Атака: {mob_loc_obj.mob.attack}"""
			"""\n"""
		f"""Защита сила: {mob_loc_obj.mob.armour_force}"""
			"""\n"""
		f"""Защита магия: {mob_loc_obj.mob.armour_magic}"""
	)
def loc_mana_hp_regenerated_info(user_obj):
	return (f"Ваша мана и здоровье обновились на 100%\nи теперь\n"
							 f"ХП: {user_obj.hp_current} из {user_obj.hp_total} \n"
							 f"МАНА: {user_obj.mana_current} из {user_obj.mana_total}")