from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


Fernandez = User(name="Fernandez", email="fernadez@gmail.com", picture="fddf")
session.add(Fernandez)

Peter = User(name="Peter", email="peter@gmail.com", picture="lkjljk")
session.add(Peter)

Basketball = Category(name="Basketball")
session.add(Basketball)

Baseball = Category(name="Baseball")
session.add(Baseball)

Frisbee = Category(name="Frisbee")
session.add(Frisbee)

Snowboarding = Category(name="Snowboarding")
session.add(Snowboarding)

Judo = Category(name="Judo")
session.add(Judo)

Cricket = Category(name="Cricket")
session.add(Cricket)

Hockey = Category(name="Hockey")
session.add(Hockey)

Googles = Item(name="Googles", category=Snowboarding, owner=Peter)
session.add(Googles)

Bat = Item(name="Bat", category=Baseball, owner=Peter)
session.add(Bat)

Stick = Item(name="Stick",
            category=Hockey,
	        owner=Fernandez,description = "Stick to play the hockey game")
session.add(Stick)

Jersey = Item(name="Jersey", category=Hockey, owner=Fernandez)
session.add(Jersey)

Snowboard = Item(name="Snowboard", category=Snowboarding, owner=Peter)
session.add(Snowboard)

Ball = Item(name="Ball",
	category=Cricket,
	owner=Fernandez,description = "Ball to play the game")
session.add(Ball)

Glouse = Item(name="Glouse",
	category=Cricket,
	owner=Fernandez,description = "Glouse is to protect your hand")
session.add(Glouse)

session.commit()
