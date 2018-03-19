from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_db_setup import Base, Users, Category, Items

engine = create_engine('sqlite:///catalogapp.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

users1 = Users(email = "userone@tester.org", username = "User1", password_hash = "nopassword")

session.add(users1)
session.commit()

category1 = Category(name = "Basketball")

session.add(category1)
session.commit()

catitem1 =  Items(name = "Rim", description = "A new basketball rim for outdoor use.", category = category1)

session.add(catitem1)
session.commit()

catitem2 =  Items(name = "Nets", description = "An old basketball net for outdoor use.", category = category1)

session.add(catitem2)
session.commit()

catitem3 =  Items(name = "Basketball", description = "Official NBA regulation basketball.", category = category1)

session.add(catitem3)
session.commit()

catitem4 =  Items(name = "Goal Post", description = "A new basketball goal post for outdoor use.", category = category1)

session.add(catitem4)
session.commit()

category2 = Category(name = "Football")

session.add(category2)
session.commit()

catitem1 =  Items(name = "Helmet", description = "A new football helmet for young teens.", category = category2)

session.add(catitem1)
session.commit()

catitem2 =  Items(name = "Football", description = "Regulation high school football.", category = category2)

session.add(catitem2)
session.commit()

catitem3 =  Items(name = "Shoulder Pads", description = "Regulation pee wee football for ages 4 to 8.", category = category2)

session.add(catitem3)
session.commit()

users2 = Users(email = "usertwo@tester.org", username = "User2", password_hash = "nopassword")

session.add(users2)
session.commit()

category3 = Category(name = "Soccer")

session.add(category3)
session.commit()

catitem1 =  Items(name = "Soccer Ball", description = "A soccer ball for outdoor use.", category = category3)

session.add(catitem1)
session.commit()

catitem2 =  Items(name = "New Nets", description = "An new basketball nets for outdoor use.", category = category1)

session.add(catitem2)
session.commit()

category4 = Category(name = "Baseball")

session.add(category4)
session.commit()

catitem1 =  Items(name = "Baseball Bat", description = "A new baseball bat.", category = category4)

session.add(catitem1)
session.commit()

category5 = Category(name = "Softball")

session.add(category5)
session.commit()

catitem1 =  Items(name = "Softball", description = "A softball.", category = category5)

session.add(catitem1)
session.commit()

category6 = Category(name = "Hockey")

session.add(category6)
session.commit()

catitem1 =  Items(name = "Hockey Stick", description = "Hockey stick for young teens.", category = category6)

session.add(catitem1)
session.commit()

category7 = Category(name = "Skating")

session.add(category7)
session.commit()

category8 = Category(name = "Kickball")

session.add(category8)
session.commit()


print "Added ALL Catalog Items!"
