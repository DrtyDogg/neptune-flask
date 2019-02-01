import unittest
from app import app, db
from app.models import User


class UserModelCase(unittest.TestCase):
    def setup(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all

    def test_password_hashing(self):
        u = User(email='test@test.com', name='user name')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
