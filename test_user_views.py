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


    def test_signup(self):
        """Test signingup a user """

        with app.test_client() as client:
            resp = client.post("/signup", 
                            data={  "username":"tester100",
                                    "password":"testing123",
                                    "email":"testing121@gmail.com",
                                    "image_url":""}, follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code,200)
            self.assertIn(f"@tester100",html)


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

    def test_logout(self):
        """Test sucessful logout """

        u1 = User.query.get(self.u1_id)
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u1.id
            resp = client.post('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn("Successfully logged out",html)
            self.assertEqual(resp.status_code, 200)




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

    def test_add_follow(self):
        """Test to see if you can follow a person """
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u1.id
            resp = client.post(f'/users/follow/{u2.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn(f"@{u2.username}",html)
            self.assertEqual(resp.status_code, 200)

    def test_stop_following(self):
        """Test to see if you can follow a person """

        u2 = User.query.get(self.u2_id)
        u4 = User.query.get(self.u4_id)
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u2.id
            resp = client.post(f'/users/stop-following/{u4.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertNotIn(f"@{u4.username}",html)
            self.assertEqual(resp.status_code, 200)


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

    def test_user_edit(self):
        """Test updating a user """

        u2 = User.query.get(self.u2_id)

        url = f"/users/profile"
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u2.id
            resp = client.post(url,data={
                                    "username":"updated",
                                    "bio": "did i update",
                                    "password" :"HASHED_PASSWORD2"},
                                    follow_redirects = True)

            html = resp.get_data(as_text=True)
            self.assertIn("@updated",html)
            self.assertIn("did i update",html)
            self.assertEqual(resp.status_code, 200)

    def test_delete_user(self):
        """Test delete user"""

        u2 = User.query.get(self.u2_id)

        url = "/users/delete"
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u2.id
            resp = client.post(url,follow_redirects = True)

            html = resp.get_data(as_text=True)
            self.assertIn("Join Warbler today.",html)
            self.assertEqual(resp.status_code, 200)


    #####################Testing status codes/html from get requests###################

    def test_signup_route(self):
        """ Test the get request for the signup page """

        with app.test_client() as client:
            resp = client.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code,200)
            self.assertIn("Join Warbler today.",html)

    def test_login_route(self):
        """ Test the get request for the login page """

        with app.test_client() as client:
            resp = client.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code,200)
            self.assertIn("Welcome back",html)

    def test_list_users(self):
        """Test list of users"""

        with app.test_client() as client:
            u1 = User.query.get(self.u1_id)

            resp = client.get("/users")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"@{u1.username}",html)

    def test_user_profile(self):
        """Test if it shows user profile correctly """

        u1 = User.query.get(self.u1_id)
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u1.id
            resp = client.get(f'/users/{u1.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn("Edit Profile",html)
            self.assertEqual(resp.status_code, 200)

    def test_show_following(self):
        """Test if it shows the list of people this user is following """

        u2 = User.query.get(self.u2_id)
        u3 = User.query.get(self.u3_id)
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u3.id
            resp = client.get(f'/users/{u3.id}/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn(f"@{u2.username}",html)
            self.assertEqual(resp.status_code, 200)

    def test_show_followers(self):
        """Test if it shows the list of followers for this user"""

        u2 = User.query.get(self.u2_id)
        u3 = User.query.get(self.u3_id)
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u2.id
            resp = client.get(f'/users/{u2.id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn(f"@{u3.username}",html)
            self.assertEqual(resp.status_code, 200)

    def test_show_user_edit(self):
        """Test if it shows the user edit page"""

        u2 = User.query.get(self.u2_id)
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u2.id
            resp = client.get('/users/profile')
            html = resp.get_data(as_text=True)

            self.assertIn("Edit Your Profile.",html)
            self.assertEqual(resp.status_code, 200)





