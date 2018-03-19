from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_db_setup import Base, Users, Category, Items

engine = create_engine('sqlite:///catalogapp.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

category1 = Category(name = "Basketball")

session.add(category1)
session.commit()

catitem1 =  Items(name = "Rim", description = "A new basketball rim for outdoor use.", category = category1)

session.add(catitem1)
session.commit()

print "Items added! "
