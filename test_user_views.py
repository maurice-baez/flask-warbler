"""User view tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from flask import Flask, session
from models import db, User, Message, Follows
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app
app.config['WTF_CSRF_ENABLED'] = False
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserViewsTestCase(TestCase):
    """Test User Views."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup("testuser", "test@test.com", "HASHED_PASSWORD","/static/images/default-pic.png")
        u2 = User.signup("test2user", "test2@test.com", "HASHED_PASSWORD2","/static/images/default-pic.png")
        u3 = User.signup("test3user", "test3@test.com", "HASHED_PASSWORD3","/static/images/default-pic.png")
        u4 = User.signup("test4user", "test4@test.com", "HASHED_PASSWORD4","/static/images/default-pic.png")

        db.session.add_all([u1,u2,u3,u4])
        db.session.commit()

        m1 = Message(text = "test message 1", user_id=u1.id)
        m2 = Message(text = "test message 2", user_id=u1.id)

        db.session.add_all([m1, m2])
        db.session.commit()

        #Test Users
        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id
        self.u4_id = u4.id

        #Test Messages
        self.m1_id = m1.id
        self.m2_id = m2.id

        u2.followers.append(u4)
        u2.followers.append(u3)
        u2.following.append(u4)
        u2.following.append(u3)
        db.session.commit()


    def tearDown(self):

        db.session.rollback()

    def test_list_users(self):
        """Test list of users"""

        with app.test_client() as client:
            u1 = User.query.get(self.u1_id)

            resp = client.get("/users")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"@{u1.username}",html)


    def test_login(self):
        """Test successful login"""
        with app.test_client() as client:
            u1 = User.query.get(self.u1_id)

            url = "/login"
            resp = client.post(url,
                                data={"username": u1.username, "password": "HASHED_PASSWORD"},
                                follow_redirects = True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"Hello, {u1.username}", html)

    def test_follower_pages(self):
        """Test if you can see the follower pages for any user """

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u3 = User.query.get(self.u3_id)
        u4 = User.query.get(self.u4_id)

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u1.id

            url = f"/users/{u2.id}/followers"
            resp = client.get(url)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"@{u3.username}",html)
            self.assertIn(f"@{u4.username}",html)

    def test_following_pages(self):
        """Test if you can see the following pages for any user """


        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u3 = User.query.get(self.u3_id)
        u4 = User.query.get(self.u4_id)

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u1.id

            url = f"/users/{u2.id}/following"
            resp = client.get(url)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"@{u3.username}",html)
            self.assertIn(f"@{u4.username}",html)


    def test_following_while_logged_out(self):
        """Test to see if you are disallowed from visiting
        a users following/follower page while logged out"""
        u2 = User.query.get(self.u2_id)

        url = f"/users/{u2.id}/following"
        with app.test_client() as client:
            resp = client.get(url,follow_redirects = True)
            html = resp.get_data(as_text=True)

        self.assertIn("Access unauthorized",html)
        self.assertEqual(resp.status_code, 200)


    def test_followers_while_logged_out(self):
        """Test to see if you are disallowed from visiting
        a users following/follower page while logged out"""
        u2 = User.query.get(self.u2_id)

        url = f"/users/{u2.id}/followers"
        with app.test_client() as client:
            resp = client.get(url,follow_redirects = True)
            html = resp.get_data(as_text=True)

        self.assertIn("Access unauthorized",html)
        self.assertEqual(resp.status_code, 200)







