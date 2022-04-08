"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY, g

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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
        m3 = Message(text = "test message 3", user_id=u2.id)

        db.session.add_all([m1, m2, m3])
        db.session.commit()

        #Test Users
        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id
        self.u4_id = u4.id

        #Test Messages
        self.m1_id = m1.id
        self.m2_id = m2.id
        self.m3_id = m3.id

        u2.followers.append(u4)
        u2.followers.append(u3)
        u2.following.append(u4)
        u2.following.append(u3)
        db.session.commit()


    def tearDown(self):

        db.session.rollback()


    def test_add_message(self):
        """Test that a user can add a message when logged in"""

        u1 = User.query.get(self.u1_id)

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u1.id

            resp = client.post('/messages/new',
                                data={"text" : "testing123"},follow_redirects = True)
            html = resp.get_data(as_text=True)

            msg = Message.query.filter_by(text="testing123").one()
            self.assertEqual(msg.text, "testing123")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testing123",html)


    def test_delete_message(self):
        """Test that a user can delete  message when logged in"""

        u1 = User.query.get(self.u1_id)


        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u1.id

            resp = client.post(f'/messages/{self.m1_id}/delete',
                                follow_redirects = True)

            html = resp.get_data(as_text=True)

            self.assertEqual(Message.query.get(self.m1_id), None)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("test message 1", html)


    def test_add_message_to_other_user(self):
        """Test that a user can't post a message to another users account"""

        u1 = User.query.get(self.u1_id)

        #Login user
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["curr_user"] = u1.id


            resp = client.post(f'/messages/{self.m3_id}/delete',
                                follow_redirects = True)
            html = resp.get_data(as_text=True)


            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized",html)
