import os
from unittest import TestCase

from models import db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Likes.query.delete()


        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.user = u

        self.client = app.test_client()
    
    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text = 'test message',
            user_id = self.user.id
        )

        db.session.add(m)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(m.text , 'test message' )
        self.assertEqual(m.user_id , self.user.id )

    def test_no_likes(self):
        """test to see if user like works"""


        m = Message(
            text = 'test message',
            user_id = self.user.id
        )

        db.session.add(m)
        db.session.commit()


        userLikes= self.user.likes
        self.assertEqual(len(userLikes), 0)

    def test_likes(self):
        """test to see if user like works"""


        m = Message(
            text = 'test message',
            user_id = self.user.id
        )

        db.session.add(m)
        db.session.commit()

        like = Likes(
            user_id = self.user.id,
            message_id = m.id
        )

        db.session.add(like)
        db.session.commit()

        userLikes= self.user.likes[0]
        self.assertEqual(userLikes, m)

    def test_2_messages(self):
        """test to see if user can have multiple messages"""

        m1 = Message(
            text = 'test message',
            user_id = self.user.id
        )
        m2 = Message(
            text = 'test message 2',
            user_id = self.user.id
        )

        db.session.add_all([m1,m2])
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(self.user.messages), 2)


       