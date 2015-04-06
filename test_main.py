import os
import unittest

from project import app, db
from config import basedir
from project.models import User, Task

TEST_DB = 'test.db'

class Alltests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def login(self, name, password):
        return self.app.post('users/', data=dict(name=name, password=password),
                             follow_redirects=True)

    def test_404_error(self):
        response = self.app.get('/not-actually-a-route/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Sorry. There\'s nothing here.', response.data)

    #def test_500_error(self):
        #bad_user = User(name='baduser',
                        #email='baduser@gmail.com',
                        #password='django')
        #db.session.add(bad_user)
        #db.session.commit()
        #response = self.login('baduser', 'django')
        #self.assertEqual(response.status_code, 500)
        #self.assertIn('Something went terribly wrong.', response.data)
        #self.assertNotIn('ValueError: Invalid salt', response.data)

if __name__ == "__main__":
    unittest.main()
