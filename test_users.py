import os
import unittest

from project import app, db, bcrypt
from config import basedir
from project.models import User, Task

TEST_DB = 'test.db'

class Alltests(unittest.TestCase):

    # if a setUp() method is defined, the test runner will run that method
    # prior to each test.
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    # if a tearDown() method is defined, the test runner will invoke that
    # method after each test.
    def tearDown(self):
        db.drop_all()

    def login(self, name, password):
        return self.app.post('users/', data=dict(name=name, password=password),
                             follow_redirects=True)

    def register(self):
        return self.app.post('users/register/',
                             data=dict(name='someuser',
                                       email='someemail@gmail.com',
                                       password='python101',
                                       confirm='python101'),
                             follow_redirects=True)

    def logout(self):
        return self.app.get('users/logout/', follow_redirects=True)

    def test_form_is_present_on_login_page(self):
        response = self.app.get('users/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Please sign in to access your task list', response.data)

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn('Invalid username or password', response.data)

    def test_user_can_login(self):
        self.register()
        response = self.login('someuser', 'python101')
        self.assertIn('You are logged in.', response.data)

    def test_logged_in_users_can_logout(self):
        self.register()
        response = self.login('someuser', 'python101')
        response = self.logout()
        self.assertIn('You are logged out. Bye.', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn('You are logged out. Bye.', response.data)

    def test_user_registration(self):
        self.app.get('users/register/', follow_redirects=True)
        response = self.register()
        self.assertIn('Thanks for registering. Please login.', response.data)

    def test_invalid_form_data(self):
        self.register()
        response = self.login('alert("alert box!")', 'foo')
        self.assertIn('Invalid username or password', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('users/register/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Please register to start a task list', response.data)

    def test_duplicate_user_registration_error(self):
        self.register()
        response = self.register()
        self.assertIn('That username or email is already in use, try again!',
                      response.data)

    def test_user_registration_field_errors(self):
        response = self.app.post('users/register/',
                                 data=dict(name='dude',
                                           email='dude',
                                           password='dudepassword',
                                           confirm=''),
                                 follow_redirects=True)
        self.assertIn('This field is required', response.data)
        self.assertIn('Invalid email address', response.data)

    def test_user_login_field_error(self):
        self.register()
        response = self.login('', 'python101')
        self.assertIn('This field is required', response.data)

    def test_string_representation_of_the_user_object(self):
        db.session.add(User("Johnny", "john@doe.com", "johnny"))
        db.session.commit()
        users = db.session.query(User).all()
        print users
        for user in users:
            self.assertEqual(user.name, 'Johnny')

    def test_default_user_role(self):
        db.session.add(User('Johnny', 'john@doe.com', 'johnny'))
        db.session.commit()
        users = db.session.query(User).all()
        print users
        for user in users:
            self.assertEqual(user.role, 'user')

if __name__ == "__main__":
    unittest.main()
