import time
import unittest
import os
import sqlite3
from users_dao import Users, make_qr


class TestUsersDao(unittest.TestCase):
    def setUp(self):
        # Create an instance of the Users class for testing
        """Set up the test environment by creating a test database."""
        self.users = Users(database='data/test_database.db')
        self.user_code_1 = 'h65ld310'
        self.user_code_2 = 'd08ae169'
        self.user_1 = ('h65ld310', 'John', 'Buck', 'jbuck@gmail.com', None)
        self.user_2 = ('d08ae169', 'Jane', 'Doe', 'jdoe@gmail.com', None)

        # Make sure to create the Users table
        self.users.make_users()
        self.users.make_logins()

    def test_make_users_table(self):
        # Ensure the Users table is created
        connection = sqlite3.connect(database='../data/test_database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'")
        result = cursor.fetchall()
        connection.close()
        self.assertEqual(len(result), 1)

    def test_make_logins_table(self):
        # Ensure the Logins table is created
        connection = sqlite3.connect(database='../data/test_database.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Logins'")
        result = cursor.fetchall()
        connection.close()
        self.assertEqual(len(result), 1)

    def test_add_user(self):
        # Ensure that user can be added successfully
        self.users.add_user(*self.user_1)
        self.users.add_user(*self.user_2)

        user_info_1 = self.users.get_info(self.user_code_1)
        user_info_2 = self.users.get_info(self.user_code_2)

        user_1 = self.user_1
        user_2 = self.user_2

        # Perform the assertion
        self.assertEqual(user_info_1, user_1)
        self.assertEqual(user_info_2, user_2)

    def test_set_status(self):
        # Ensure that user status can be set correctly
        self.users.add_user(*self.user_1)
        self.users.add_user(*self.user_2)

        # Initial status is None
        self.assertIsNone(self.users.get_info(self.user_code_1)[4])

        # Set status to Active
        self.users.set_status(self.user_code_1)
        self.assertEqual(self.users.get_info(self.user_code_1)[4], 'Active')

        # Set status to Inactive
        self.users.set_status(self.user_code_1)
        self.assertEqual(self.users.get_info(self.user_code_1)[4], 'Inactive')

    def test_login_and_logout(self):
        # Ensure that user can be logged in and out successfully
        timestamp = '2023-07-17 12:34:56'
        self.users.add_user(*self.user_1)
        self.users.add_user(*self.user_2)

        # User logs in
        status = self.users.set_status(self.user_code_1)
        # self.users.set_status(self.user_1[0])
        if status == 'Active':
            self.users.login(timestamp, self.user_code_1)
            time.sleep(1)  # Add a small delay between logins to ensure unique timestamps
            self.assertEqual(self.users.get_info(self.user_code_1)[4], 'Active')
        else:
            # User logs out
            self.users.logout(self.user_code_1, timestamp)
            time.sleep(1)  # Add a small delay between logins to ensure unique timestamps
            self.assertEqual(self.users.get_info(self.user_code_1)[4], 'Inactive')

    def test_get_whitelist(self):
        # Ensure that get_whitelist returns a list of all user codes
        self.users.add_user(*self.user_1)
        self.users.add_user(*self.user_2)

        whitelist = self.users.get_whitelist()
        self.assertIn(self.user_code_1, whitelist)
        self.assertIn(self.user_code_2, whitelist)

    def tearDown(self):
        # Clean up any test files created
        os.remove('../data/qr_images/JohnBuck.jpg')
        os.remove('../data/qr_images/JaneDoe.jpg')
        os.remove('../data/test_database.db')


if __name__ == '__main__':
    unittest.main()
