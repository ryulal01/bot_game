from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///game_tg.db')
Session = sessionmaker(autoflush = False, bind = engine)
session = Session()
