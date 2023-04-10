"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Message, Follows


db.drop_all()
db.create_all()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/messages.csv') as messages:
    db.session.bulk_insert_mappings(Message, DictReader(messages))

with open('generator/follows.csv') as follows:
    db.session.bulk_insert_mappings(Follows, DictReader(follows))

db.session.commit()

# changed bg image because other one doesn't work
for user in User.query.all():
    user.header_image_url = "/static/images/warbler-hero.jpg"

db.session.commit()

u = User.signup(username='catman', email='skvaladez@yahoo.com', password='goodpassword', image_url='https://i.natgeofe.com/n/548467d8-c5f1-4551-9f58-6817a8d2c45e/NationalGeographic_2572187_square.jpg')
db.session.add(u)
db.session.commit()
