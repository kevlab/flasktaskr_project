import os
import unittest
from datetime import date

from project import app, db
from config import basedir
from project.models import Task

TEST_DB = 'test.db'

class AllTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def add_tasks(self):
        db.session.add(Task("Run around in circles",
                            date(2015, 5, 22),
                            10,
                            date(2015, 4, 21),
                            1,
                            1))
        db.session.commit()

        db.session.add(Task("Purchase Real Python",
                            date(2015, 6, 22),
                            10,
                            date(2015, 5, 21),
                            1,
                            1))
        db.session.commit()

    def test_collection_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/tasks/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        self.assertIn("Run around in circles", response.data)
        self.assertIn("Purchase Real Python", response.data)

    def test_resource_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/tasks/2', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')
        self.assertNotIn("Run around in circles", response.data)
        self.assertIn("Purchase Real Python", response.data)

    def test_invalid_resource_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/tasks/3', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, 'application/json')
        self.assertIn("Element does not exist", response.data)

if __name__ == "__main__":
    unittest.main()
