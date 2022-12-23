from datetime import datetime
import random

from sqlalchemy import Column, String, Integer, DateTime, \
	ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import relationship, declarative_base

from app.utils import LOCATIONS, ITEMS, MOBS
from config.db import engine, session

Base = declarative_base()


class Item(Base):
	__tablename__ = 'items'

	id = Column(Integer, primary_key = True)
	name = Column(String(20), unique = True,
				  nullable = False)
	cost = Column(Integer, nullable = False)
	cost_to_sale = Column(Integer, nullable = False)
	item_type = Column(
		Enum('Оружие', 'Броня', 'Шлем', 'Сапоги', 'Наручи', 'Зелье'))
	hp_add = Column(Integer, nullable = False)
	mana_add = Column(Integer, nullable = False)
	attack_force_add = Column(Integer, nullable = False)
	attack_magic_add = Column(Integer, nullable = False)
	armour_force_add = Column(Integer, nullable = False)
	armour_magic_add = Column(Integer, nullable = False)
	req_level = Column(Integer, nullable = False)

	item_on_loc = relationship("ItemsOnLoc", backref = "item")

	@staticmethod
	def prepopulate_items():
		items_obj = session.query(Item).all()
		if not items_obj:
			try:
				obj_to_commit = [Item(
					id = item.get('id'),
					name = item.get('name'),
					cost = item.get('cost'),
					cost_to_sale = item.get('cost_to_sale'),
					item_type = item.get('item_type'),
					hp_add = item.get('hp_add'),
					mana_add = item.get('mana_add'),
					attack_force_add = item.get('attack_force_add'),
					attack_magic_add = item.get('attack_magic_add'),
					armour_force_add = item.get('armour_force_add'),
					armour_magic_add = item.get('armour_magic_add'),
					req_level = item.get('req_level'),
				) for item in
					ITEMS]
				session.bulk_save_objects(obj_to_commit)
				session.commit()
			except Exception as e:
				print('Ошибка при загрузке items в базу')
				print(e)
				session.rollback()


class Mob(Base):
	__tablename__ = 'mobs'
	id = Column(Integer, primary_key = True)
	hp_total = Column(Integer, nullable = False)
	req_level = Column(Integer, nullable = False)
	attack_type = Column(Enum('Магическая', 'Силовая'))
	attack = Column(Integer, nullable = False)
	armour_force = Column(Integer, nullable = False)
	armour_magic = Column(Integer, nullable = False)

	mob_user_on_loc = relationship("MobLocUser", backref = "mob")

	@staticmethod
	def prepopulate_mobs():
		mobs_obj = session.query(Mob).all()
		if not mobs_obj:
			try:
				obj_to_commit = [Mob(
					id = mob.get('id'),
					hp_total = mob.get('hp_total'),
					req_level = mob.get('req_level'),
					attack_type = mob.get('attack_type'),
					attack = mob.get('attack'),
					armour_force = mob.get('armour_force'),
					armour_magic = mob.get('armour_magic'),
				) for mob in
					MOBS]
				session.bulk_save_objects(obj_to_commit)
				session.commit()
			except Exception as e:
				print('Ошибка при загрузке mobs в базу')
				print(e)
				session.rollback()


class MobLocUser(Base):
	__tablename__ = 'mob_loc_user'
	id = Column(Integer, primary_key = True)
	mob_rel = Column(Integer, ForeignKey('mobs.id'),
					 nullable = False)
	location_rel = Column(Integer, ForeignKey('locations.id'),
						  nullable = False)
	user_rel = Column(Integer, ForeignKey('persons.id'), nullable = False)

	hp_current_mob = Column(Integer, nullable = False)

	__table_args__ = (
		UniqueConstraint(
			'mob_rel',
			'location_rel',
			'user_rel',
			name = 'uniq_mob_loc_user'),
	)

	@staticmethod
	def generate_or_get_mob(user):
		mob_on_loc_obj = session.query(
			MobLocUser).filter(
			MobLocUser.user_rel == user.id,
			MobLocUser.location_rel == user.person_curr_loc.id,
		).first()
		if not mob_on_loc_obj:
			random_mob_obj = random.choice(session.query(Mob).all())
			mob_on_loc_obj = MobLocUser(
				mob_rel = random_mob_obj.id,
				location_rel = user.person_curr_loc.id,
				user_rel = user.id,
				hp_current_mob = random_mob_obj.hp_total,
			)
			try:
				session.add(mob_on_loc_obj)
				session.commit()
			except Exception as e:
				print(
					'Ошибка при загрузке рандомного моба на локацию, в базу')
				print(e)
				session.rollback()
		return mob_on_loc_obj


class Location(Base):
	__tablename__ = 'locations'

	id = Column(Integer, primary_key = True)
	name = Column(String(20), unique = True, nullable = False)
	coord_x = Column(Integer, nullable = False)
	coord_y = Column(Integer, nullable = False)
	location_type = Column(Enum('Город', 'Подземелье'))

	person_base_city = relationship("Person", foreign_keys = "Person.base_city",
									backref = "person_base_city")
	person_curr_loc = relationship("Person", foreign_keys = "Person.curr_loc",
								   backref = "person_curr_loc")

	item_on_loc = relationship("ItemsOnLoc", backref = "location")
	loc_near_first = relationship("LocationNear",
								  foreign_keys = 'LocationNear.location_first',
								  backref = "loc_first")
	loc_near_second = relationship("LocationNear",
								   foreign_keys = 'LocationNear.location_second',
								   backref = "loc_second")

	@staticmethod
	def prepopulate_locations():
		locations_obj = session.query(Location).all()
		if not locations_obj:
			try:
				obj_to_commit = [Location(
					id = loc.get('loc_id'),
					name = loc.get('name'),
					coord_x = loc.get('coord_x'),
					coord_y = loc.get('coord_y'),
					location_type = loc.get('location_type'),
				) for loc in
					LOCATIONS]
				session.bulk_save_objects(obj_to_commit)
				session.commit()
			except Exception as e:
				print('Ошибка при загрузке локаций в базу')
				print(e)
				session.rollback()


class LocationNear(Base):
	__tablename__ = 'location_near'
	id = Column(Integer, primary_key = True)
	location_first = Column(Integer, ForeignKey('locations.id'),
							nullable = False)
	location_second = Column(Integer, ForeignKey('locations.id'),
							 nullable = False)
	step_to_go = Column(Integer, nullable = False)

	__table_args__ = (
		UniqueConstraint(
			'location_first',
			'location_second',
			name = 'loc_near_unique'),
	)

	@staticmethod
	def prepopulate_locations_near():
		locations_obj = session.query(
			Location).all()
		if not session.query(
				LocationNear).all():
			for loc in locations_obj:
				for loc_2 in locations_obj:
					if loc != loc_2:

						cord_x = (abs(loc.coord_x - loc_2.coord_x))
						cord_y = (abs(loc.coord_y - loc_2.coord_y))
						if cord_x <= 10 or cord_y <= 10:
							try:
								session.add(
									LocationNear(location_first = loc.id,
												 location_second = loc_2.id,
												 step_to_go = min(cord_x,
																  cord_y)))
								session.commit()
							except Exception as e:
								print(
									'Ошибка при загрузке локаций куда можно переместиться, в базу')
								print(e)
								session.rollback()

	@staticmethod
	def get_near_locations(actual_location_id):
		return session.query(
			LocationNear).filter(
			LocationNear.location_first == actual_location_id)


class Person(Base):
	__tablename__ = 'persons'
	id = Column(Integer, primary_key = True)
	user_id_tg = Column(Integer, unique = True, nullable = False)
	created_on = Column(DateTime(), default = datetime.now)
	updated_on = Column(DateTime(), default = datetime.now,
						onupdate = datetime.now)
	nick_name = Column(String(20), unique = True, nullable = False)
	level = Column(Integer, nullable = False)

	hp_total = Column(Integer, nullable = False)
	hp_current = Column(Integer, nullable = False)

	mana_total = Column(Integer, nullable = False)
	mana_current = Column(Integer, nullable = False)

	race_selected = Column(Enum('Сильные', 'Магические', 'Балансированные'))

	money = Column(Integer, nullable = False)
	attack_force_basic = Column(Integer, nullable = False)
	attack_magic_basic = Column(Integer, nullable = False)
	experience_on_level = Column(Integer, nullable = False)
	armour_force_basic = Column(Integer, nullable = False)
	armour_magic_basic = Column(Integer, nullable = False)
	base_city = Column(Integer, ForeignKey('locations.id'), nullable = False)
	curr_loc = Column(Integer, ForeignKey('locations.id'), nullable = False)

	actual_arm_from_item = Column(Integer, ForeignKey('items.id'))  # оружие
	actual_armour_from_item = Column(Integer, ForeignKey('items.id'))  # броня
	actual_helm_from_item = Column(Integer, ForeignKey('items.id'))  # шлем
	actual_boot_from_item = Column(Integer, ForeignKey('items.id'))  # обувь
	actual_gloves_from_item = Column(Integer,
									 ForeignKey('items.id'))  # перчатки


class Inventory(Base):
	__tablename__ = 'inventories'
	id = Column(Integer, primary_key = True)
	user_rel = Column(Integer, ForeignKey('persons.id'))
	item_rel = Column(Integer, ForeignKey('items.id'))
	quantity = Column(Integer, nullable = False)
	usage = Column(Integer, nullable = False)
	__table_args__ = (
		UniqueConstraint(
			'user_rel',
			'item_rel',
			name = 'inventory_user_item_unique'),
	)


class ItemsOnLoc(Base):
	__tablename__ = 'items_on_loc'
	id = Column(Integer, primary_key = True)
	loc_rel = Column(Integer, ForeignKey('locations.id'))
	item_rel = Column(Integer, ForeignKey('items.id'))
	quantity = Column(Integer, nullable = False)
	__table_args__ = (
		UniqueConstraint(
			'loc_rel',
			'item_rel',
			name = 'items_on_loc_unique'),
	)

	@staticmethod
	def prepopulate_items_on_loc_city():
		locations_city_obj = session.query(
			Location).filter(Location.location_type == 'Город').all()
		items_obj = session.query(Item).all()
		if locations_city_obj and not session.query(ItemsOnLoc).all():
			for location_city_obj in locations_city_obj:
				try:
					obj_to_commit = [ItemsOnLoc(
						loc_rel = location_city_obj.id,
						item_rel = item_obj.id,
						quantity = 9,
					) for item_obj in
						items_obj]
					session.bulk_save_objects(obj_to_commit)
					session.commit()
				except Exception as e:
					print('Ошибка при загрузке items on loc city в базу')
					print(e)
					session.rollback()

	@staticmethod
	def prepopulate_items_on_loc_underground():
		items_obj = session.query(Item)
		locations_underground_obj = session.query(
			Location).filter(Location.location_type == 'Подземелье')
		items_on_loc_underground = session.query(
			ItemsOnLoc).filter(ItemsOnLoc.loc_rel.in_(
			[loc.id for loc in locations_underground_obj]))
		items_on_loc_underground.delete()
		items_on_loc_underground = session.query(
			ItemsOnLoc).filter(ItemsOnLoc.loc_rel.in_(
			[loc.id for loc in locations_underground_obj]))

		if locations_underground_obj:
			for location_underground_obj in locations_underground_obj:
				try:
					obj_to_commit = ItemsOnLoc(
						loc_rel = location_underground_obj.id,
						item_rel = random.choice(items_obj.all()).id,
						quantity = 1,
					)
					session.add(obj_to_commit)
					session.commit()
				except Exception as e:
					print('Ошибка при загрузке items on loc underground в базу')
					print(e)
					session.rollback()


def init_db():
	Base.metadata.create_all(bind = engine)
	Location.prepopulate_locations()
	Item.prepopulate_items()
	Mob.prepopulate_mobs()
	ItemsOnLoc.prepopulate_items_on_loc_city()
	ItemsOnLoc.prepopulate_items_on_loc_underground()
	LocationNear.prepopulate_locations_near()
