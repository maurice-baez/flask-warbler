"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


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

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="test2user",
            password="HASHED_PASSWORD2"
        )
        db.session.add_all([u1,u2])
        db.session.commit()

        self.u1 = u1
        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        # u = User(
        #     email="test@test.com",
        #     username="testuser",
        #     password="HASHED_PASSWORD"
        # )

        # db.session.add(u)
        # db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)

    def test_repr(self):
        """Does the repr return the correct info """
        self.assertEqual(self.u1.__repr__(),f"<User #{self.u1.id}: testuser, test@test.com>")

    def test_is_following(self):
        """Does our is_following method work properly """

        self.assertFalse(self.u1.is_following(self.u2))

        self.u1.following.append(self.u2)

        self.assertTrue(self.u1.is_following(self.u2))



    def test_is_followed_by(self):
        """Does our is_followed_by method work properly """

        self.assertFalse(self.u1.is_followed_by(self.u2))

        self.u1.followers.append(self.u2)

        self.assertTrue(self.u1.is_followed_by(self.u2))

    def test_signup(self):
        """Does User.signup successfully create a new user """

        new_user = User.signup("testing1", "testing1@gmail.com", "123456", "/static/images/default-pic.png")
        self.assertTrue(User.query.filter_by(username="testing1").one_or_none())


    def test_fail_signup(self):
        """Tests failed signups based on uniqueness constraints"""
        new_user2 = User.signup("testuser", "test@test.com","123456", "/static/images/default-pic.png")
        with self.assertRaises(IntegrityError):
            db.session.commit()

        


    
    
    



