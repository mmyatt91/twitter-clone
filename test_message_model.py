import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 12345
        user = User.signup("immatest", "imtesting@abc.com", "lilred", None)
        user.id = self.uid
        db.session.commit()

        self.user = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_model_msg(self):
        
        msg = Message(
            text="warble warble",
            user_id=self.uid
        )

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(self.user.messages[0].text, "warble warble")

    def test_like_msg(self):
        msg1 = Message(
            text="warble warble",
            user_id=self.uid
        )

        msg2 = Message(
            text="I got something to say.",
            user_id=self.uid 
        )

        user = User.signup("immatest2", "wetesting2@email.com", "lilorange", None)
        uid = 12345
        user.id = uid
        db.session.add_all([msg1, msg2, user])
        db.session.commit()

        user.likes.append(msg1)

        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, msg1.id)


        