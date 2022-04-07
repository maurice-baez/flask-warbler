"""User view tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, do_login

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

        db.session.add_all([u1,u2])
        db.session.commit()

        m1 = Message(text = "test message 1", user_id=u1.id)
        m2 = Message(text = "test message 2", user_id=u1.id)

        db.session.add_all([m1, m2])
        db.session.commit()

        self.u1 = u1
        self.u2 = u2
        self.m1 = m1
        self.m2 = m2

        do_login(self.u1)

        self.client = app.test_client()


    def tearDown(self):

        db.session.rollback()

    def test_list_users(self):
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"@{self.u1.username}",html)

            
