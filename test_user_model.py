"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_is_following(self):
        """test if user following is correct"""


        u1 = User(
            email="test@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add_all([u1, u2])
        db.session.commit()

        f = Follows(user_being_followed_id=u2.id, user_following_id=u1.id)

        db.session.add(f)
        db.session.commit()


        following = u1.following[0]
        self.assertEqual(following.id, u2.id)

    def test_is_not_following(self):
        """test if user is not following is correct"""


        u1 = User(
            email="test@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add_all([u1, u2])
        db.session.commit() 

        self.assertEqual(len(u1.following), 0)

    def test_is_followed(self):
        """test if user following is correct"""


        u1 = User(
            email="test@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add_all([u1, u2])
        db.session.commit()

        f = Follows(user_being_followed_id=u1.id, user_following_id=u2.id)

        db.session.add(f)
        db.session.commit()


        followed = u1.followers[0]
        self.assertEqual(followed.id, u2.id)

    def test_is_not_followed(self):
        """test if user is not following is correct"""


        u1 = User(
            email="test@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add_all([u1, u2])
        db.session.commit() 

        self.assertEqual(len(u1.followers), 0)


    def test_user_model_signup(self):
        """Does basic model work?"""

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(u.username, 'testuser')
        self.assertEqual(u.email, "test@test.com")
        self.assertTrue(len(u.password) > len("HASHED_PASSWORD"))
  
    def test_user_model_signup_unique(self):
        """test to see if signup has to be unique"""

        u1 = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
        )
        u2 = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
        )

        try:
            db.session.add_all([u1, u2])
            db.session.commit()
            self.assertTrue(False)
        except:
            self.assertTrue(True)

    def test_user_authenticate(self):
        """test if authenticator returns correct user"""

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
        )

        db.session.add(u)
        db.session.commit()

        u2 = User.authenticate(
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.assertEqual(u,u2)
    
    def test_user_authenticate_incorrect_username(self):
        """test if authenticator returns correct user"""

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
        )

        db.session.add(u)
        db.session.commit()

        u2 = User.authenticate(
            username="incorrectusername",
            password="HASHED_PASSWORD"
        )

        self.assertTrue(u != u2)
    
    def test_user_authenticate_incorrect_password(self):
        """test if authenticator returns correct user"""

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
        )

        db.session.add(u)
        db.session.commit()

        u2 = User.authenticate(
            username="testuser",
            password="INCORRECT_PASSWORD"
        )

        self.assertTrue(u != u2)