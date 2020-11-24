"""User View tests."""
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages"""

    def setUp(self):
        """Creates test client."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="bethebest", 
                                    email="bethebest@yes.com", 
                                    password="thebest", 
                                    image_url=None)
        
        self.testuser_id = 2426
        self.testuser.id = self.testuser_id

        """Adds sample data."""

        self.u1 = User.signup("betheone", "betheone@yes.com", "theone", None)
        self.u1_id = 135
        self.u1.id = self.u1_id
        self.u2 = User.signup("bethefirst", "bethefirst@yes.com", "thefirst", None)

        db.session.commit()

    def tearDown(self):
        """Resets everything after test are run"""
        resp = super().tearDown()
        db.session.rollback()
        return resp
    
    def test_list_users(self):
        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@bethebest", str(resp.data))
            self.assertIn("@betheone", str(resp.data))
            self.assertIn("@bethefirst", str(resp.data))

    def test_show_user(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@bethebest", str(resp.data))
    
    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1_id)
        f2 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id)

    
    def test_show_following(self):
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/following")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@bethebest", str(resp.data))
            self.assertIn("@betheone", str(resp.data))
            self.assertNotIn("@bethefirst", str(resp.data))
    
    def test_show_followers(self):
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/followers")

            self.assertIn("@bethebest", str(resp.data))
            self.assertIn("@betheone", str(resp.data))
            self.assertNotIn("@bethefirst", str(resp.data))        

    def test_add_follow(self):
        u = User(id=2426, email="iamtheone@246.com", username="iamtheone", image_url=None)
        db.session.add(u)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/users/follow/2426", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
    
    def setup_likes(self):
        m1 = Message(text="warble warble", user_id=self.testuser_id)
        m2 = Message(text="and warble some more", user_id=self.testuser_id)
        m3 = Message(id=3486, text="you warble", user_id=self.u1_id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        l1 = Likes(user_id=self.testuser_id, message_id=3486)

        db.session.add(l1)
        db.session.commit()
    
    def test_add_like(self):
        m = Message(id=1991, text="borninthechi", username="iamtheone", user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/messages/1991/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
           
            likes = Likes.query.filter(Likes.message_id==1991).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)
    
    def test_show_like(self):
        self.setup_likes()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")
            self.assertEqual(resp.status_code, 200)

            self.assertIn("@bethebest", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            self.assertIn("1", found[0].text)
            self.assertIn("2", found[1].next)
