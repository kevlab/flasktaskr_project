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

    def create_user(self):
        new_user = User(name='testuser',
                        email='testuser@hotmail.com',
                        password=bcrypt.generate_password_hash('python'))
        db.session.add(new_user)
        db.session.commit()

    def create_admin_user(self):
        new_user = User(name='Superman',
                        email='admin@hotmail.com',
                        password=bcrypt.generate_password_hash('allpowerful'),
                        role='admin')
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        return self.app.post('tasks/add/',
                             data=dict(name='Go buy milk',
                                       due_date='04/21/2015',
                                       priority='1',
                                       posted_date='03/21/1015',
                                       status='1'),
                             follow_redirects=True)

    def test_logged_in_users_can_access_tasks_page(self):
        self.register()
        self.login('someuser', 'python101')
        response = self.app.get('tasks/tasks/', follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertIn('Add a new task', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/tasks/', follow_redirects=True)
        self.assertIn('You need to login first', response.data)

    def test_users_can_add_tasks(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn('New entry was successfully posted. Thanks.',
                      response.data)

    def test_users_cannot_add_tasks_when_error(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.app.post('tasks/add/', data=dict(name='Go buy milk',
                                                   due_date='',
                                                   priority='1',
                                                   posted_date='03/21/1015',
                                                   status='1'),
                                 follow_redirects=True)
        self.assertIn('This field is required.', response.data)

    def test_users_can_complete_tasks(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("tasks/complete/1/", follow_redirects=True)
        self.assertIn('The task was marked as complete.', response.data)

    def test_users_can_delete_tasks(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("tasks/delete/1/", follow_redirects=True)
        self.assertIn('The task was deleted.', response.data)

    def test_users_cannot_complete_tasks_they_did_not_create_themselves(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register()
        self.login('someuser', 'python101')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.app.get("tasks/complete/1/", follow_redirects=True)
        self.assertIn('You can only update tasks that belong to you',
                      response.data)

    def test_users_cannot_delete_tasks_they_did_not_create_themselves(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register()
        self.login('someuser', 'python101')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.app.get("tasks/delete/1/", follow_redirects=True)
        self.assertIn('You can only delete tasks that belong to you',
                      response.data)

    def test_admin_can_complete_tasks_they_did_not_create_themselves(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.app.get("tasks/complete/1/", follow_redirects=True)
        self.assertNotIn('You can only update tasks that belong to you',
                         response.data)

    def test_admin_can_delete_tasks_they_did_not_create_themselves(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.app.get("tasks/delete/1/", follow_redirects=True)
        self.assertNotIn('You can only delete tasks that belong to you',
                         response.data)

    def test_string_representation_of_the_task_object(self):
        from datetime import date
        db.session.add(Task("Run around in circles",
                            date(2015, 1, 22),
                            10,
                            date(2015, 1, 05),
                            1,
                            1))
        db.session.commit()
        tasks = db.session.query(Task).all()
        print tasks
        for task in tasks:
            self.assertEqual(task.name, 'Run around in circles')

    def test_task_template_displays_logged_in_user_name(self):
        self.register()
        self.login('someuser', 'python101')
        response = self.app.get('tasks/tasks/', follow_redirects=True)
        self.assertIn('someuser', response.data)

    def test_users_cannot_see_links_for_tasks_they_did_not_create(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register()
        response = self.login('someuser', 'python101')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.assertNotIn('Mark as Complete', response.data)
        self.assertNotIn('Delete', response.data)

    def test_users_can_see_links_for_tasks_they_did_create(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register()
        self.login('someuser', 'python101')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn('tasks/complete/2/', response.data)
        self.assertIn('tasks/delete/2/', response.data)

    def test_admin_can_see_links_for_all_tasks(self):
        self.create_user()
        self.login('testuser', 'python')
        self.app.get('tasks/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn('tasks/complete/1/', response.data)
        self.assertIn('tasks/delete/1/', response.data)
        self.assertIn('tasks/complete/2/', response.data)
        self.assertIn('tasks/delete/2/', response.data)


if __name__ == "__main__":
    unittest.main()
