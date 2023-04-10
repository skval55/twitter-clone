"""test user veiws"""


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCaseLoggedIn(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)

        db.session.commit()

        msg = Message(text="test message",
                                    user_id = self.testuser.id)
        
        db.session.add(msg)
        db.session.commit()

        self.testmsg = msg

        follow = Follows(user_being_followed_id=self.testuser.id, user_following_id=self.testuser2.id)

        db.session.add(follow)
        db.session.commit()

        self.testfollow = follow

    def test_users_index(self):
        """test user user search up"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

           
            resp = c.get("/users?q=test")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>@testuser</p>', html)
    
    def test_users_index_not_found(self):
        """test user user search up"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

           
            resp = c.get("/users?q=impossible")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h3>Sorry, no users found</h3>', html)

    def test_like(self):
        """test like route"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.post(f"/users/add_like/{self.testmsg.id}", follow_redirects=True)
        html = resp.get_data(as_text=True)   

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<p>@testuser</p>', html)
           
    def test_follower_page_logged_in(self):
        """test to see the following page of another user"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f'/users/{self.testuser2.id}/following')
        html = resp.get_data(as_text=True)   

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<p>@testuser</p>', html)

    def test_follower_page_logged_out(self):
        """test to see the following page of another user logged out"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

        resp = c.get(f'/users/{self.testuser2.id}/following', follow_redirects=True)
        html = resp.get_data(as_text=True)   

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)

    def test_follow_logged_in(self):
        """test if you can follow user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.post(f'/users/follow/{self.testuser2.id}', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<p>@testuser2</p>', html)

    def test_follow_logged_out(self):
        """test if you can follow user logged out"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

        resp = c.post(f'/users/follow/{self.testuser2.id}', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)

    def test_stop_follow_logged_in(self):
        """test if you can stop following user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2.id

        resp = c.post(f'/users/stop-following/{self.testuser.id}', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h4 id="sidebar-username">@testuser2</h4>', html)

    def test_stop_follow_logged_out(self):
        """test if you can stop following user logged out"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

        resp = c.post(f'/users/stop-following/{self.testuser.id}', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)
        
    def test_user_delete(self):
        """test to see if you can delete profile while logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2.id
        
        resp = c.post('/users/delete', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)
        
    def test_user_delete_logged_out(self):
        """test to see if you can delete profile while logged out"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None
        
        resp = c.post('/users/delete', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)

    def test_edit_user(self):
        """test to see if you can edit user profile"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.post('/users/profile', data={'username':'catboy', 'image_url':'cool_image.jpeg', 'header_image_url':'cool.jpeg','email':'skate@skate.com','bio':'skate or die', 'password':'testuser' }, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<img src="cool_image.jpeg"', html)
        self.assertIn('<h4 id="sidebar-username">@catboy</h4>', html)
        self.assertIn('<p>skate or die</p>', html)
   
    def test_edit_user_logged_out(self):
        """test to see if you can edit user profile logged out"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None

        resp = c.post('/users/profile', data={'username':'catboy', 'image_url':'cool_image.jpeg', 'header_image_url':'cool.jpeg','email':'skate@skate.com','bio':'skate or die', 'password':'testuser' }, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)