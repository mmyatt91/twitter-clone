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

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user_1 = User.signup("test_u1", "123@abc.com", "iamone", None)
        user_1id = 123
        user_1.id = user_1id

        user_2 = User.signup("test_u2", "456@def.com", "iamtwo", None)
        user_2id = 456
        user_2.id = user_2id

        db.session.commit()

        user_1 = User.query.get(user_1id)
        user_2 = User.query.get(user_2id)

        self.user_1 = user_1
        self.user_1id = user_1id

        self.user_2 = user_2
        self.user_2id = user_2id

        self.client = app.test_client()

    def teardown(self):
        resp = super().teardown()
        db.session.rollback()
        return resp

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
    
    # Tests for Following

    def test_user_follows(self):
        """Allows user_2 to follow user_1"""
        self.user_1.following.append(self.user_2)
        db.session.commit()

        self.assertEqual(len(self.user_1.followers), 0)
        self.assertEqual(len(self.user_1.following), 1)
        self.assertEqual(len(self.user_2.followers), 0)
        self.assertEqual(len(self.user_2.following), 1)

    def test_is_following(self):
        """Test is_following functionality"""
        self.user_1.following.append(self.user_2)
        db.session.commit()

        self.assertTrue(self.user_1.is_following(self.user_2))
        self.assertFalse(self.user_2.is__following(self.user_1))

    def test_is_followed_by(self):
        """Test is_followed_by functionality"""
        self.user_1.following.append(self.user_2)
        db.session.commit()

        self.assertTrue(self.user_1.is_followed_by(self.user_2))
        self.assertFalse(self.user_2.is__followed_by(self.user_1)) 

    #Tests for Sign-ups

    def test_valid_sign_up(self):
        user_test = User.signup("wetest", "wetest@123.com", "wetest91", None)
        uid = 123456
        user_test.id = uid
        db.session.commit()

        user_test = User.query.get(uid)
        self.assertEqual(user_test.username, "wetest")
        self.assertEqual(user_test.email, "wetest@123.com")
        self.assertEqual(user_test.password, "wetest91")
    
    def test_invalid_username(self):
        invalid = User.signup(None, "wetest@123.com", "wetest91", None)
        uid = 123456
        invalid.id = uid 
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_email(self):
        invalid = User.signup("wetest", None, "wetest91", None)
        uid = 123456
        invalid.id = uid 
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password(self):
        with self.assertRaises(ValueError) as context:
            db.session.commit()
    

    #Tests for Authentication
    def test_valid_authentication(self):
        u = User.authenticate(self.user_1.username, "martinmyman")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.user_1id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("notagoodusername", "martinmyman"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user_1.username, "notagoodpassword"))