"""
Author: Jacob Pitsenberger
Program: users_dao.py
Version: 1.0
Project: QR Code Login System
Date: 7/18/2023
Purpose: This program is used to create the database, its tables, user qr codes, and act as an object for
any functionality that requires access to the database so that it can be interacted with in some way.
Uses: N/A
"""
from pathlib import Path
from typing import Optional, Tuple
import qrcode
import sqlite3
import numpy as np
import os

QR_IMG_PATH = Path("data/qr_images")

def make_qr_dir() -> None:
    """
    This checks if the directory exists and if not makes it.
    """
    if not os.path.exists(QR_IMG_PATH):
        QR_IMG_PATH.mkdir()

def make_qr(data: str, filename: str) -> None:
    """Generate a QR code with the inputted data and store it in an image under the inputter filename.

    Args:
        data (str): The data to be encoded in the QR code.
        filename (str): The filename for saving the generated QR code image.

    Returns:
        None
    """

    # Create QRCode object
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    # Add the data parameter to the qr
    qr.add_data(data)

    # Put data into a qr code array
    qr.make(fit=True)

    # Make an image of the QR code with a white background and black fill.
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Save the image under the filename parameter
    qrPath = os.path.join(QR_IMG_PATH, filename)
    img.save(qrPath)


def handle_sqlite_error(error: sqlite3.Error) -> None:
    """Handle SQLite errors by raising an exception with the error message.

    Args:
        error (sqlite3.Error): The SQLite error object.

    Raises:
        Exception: The raised exception with the SQLite error message.
    """
    error_msg = 'SQLite error: %s' % (' '.join(error.args))
    print(error_msg)
    raise Exception(error_msg)


# Variable for Users create table statement
users_table = (''' CREATE TABLE IF NOT EXISTS Users
                (  code      TEXT PRIMARY KEY NOT NULL UNIQUE,
                   firstName TEXT NOT NULL,
                   lastName  TEXT NOT NULL,
                   email     TEXT NOT NULL,
                   status    TEXT
                );''')

# Variable for Users create table statement
logins_table = (''' CREATE TABLE IF NOT EXISTS Logins
                (   timestamp   TEXT PRIMARY KEY NOT NULL,
                    logoutTime  TEXT,
                    userCode    TEXT NOT NULL,
                    FOREIGN KEY(userCode) REFERENCES Users(code)
                );''')


class Users:
    def __init__(self, database: str = 'data/user_database.db', qr_img_path: Path = QR_IMG_PATH) -> None:
        """Initialize the Users object and create the necessary tables in the database.

        Args:
            database (str): The path to the SQLite database.

        Returns:
            None
        """
        self.database = os.path.join(os.path.dirname(__file__), database)
        self.qr_img_path = QR_IMG_PATH
        make_qr_dir()

        # Initialize the database tables
        self.make_users()
        self.make_logins()

        # Add some entries to the users table for testing
        self.add_user('h65ld310', 'John', 'Buck', 'jbuck@gmail.com', None)
        self.add_user('d08ae169', 'Jane', 'Doe', 'jdoe@gmail.com', None)

    def connect(self) -> sqlite3.Connection:
        """Get a connection object for the database.

        Returns:
            sqlite3.Connection: The connection object.
        """
        connection = sqlite3.connect(self.database)
        return connection

    def make_users(self) -> None:
        """Connect to the database and create the Users table if it doesn't exist.

        Returns:
            None
        """
        # Use a context manager (with statement) for the connection
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(users_table)
                # Added per gpt
                connection.commit()
            except sqlite3.Error as er:
                # print('SQLite error: %s' % (' '.join(er.args)))
                # print("Exception class is: ", er.__class__)
                # print('SQLite traceback: ')
                # exc_type, exc_value, exc_tb = sys.exc_info()
                # print(traceback.format_exception(exc_type, exc_value, exc_tb))
                handle_sqlite_error(er)

    def make_logins(self) -> None:
        """Connect to the database and create the Logins table."""
        # Use a context manager (with statement) for the connection
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(logins_table)
                connection.commit()
            except sqlite3.Error as er:
                handle_sqlite_error(er)

    def add_user(self, code: str, first_name: str, last_name: str, email: str, status: Optional[str]) -> None:
        """Add a record to the Users table if an entry doesn't already exist.

        Args:
            code (str): The user code.
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            email (str): The email address of the user.
            status (str, optional): The status of the user (e.g., "Active" or "Inactive").

        Returns:
            None
        """
        # Use a context manager (with statement) for the connection
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT OR IGNORE INTO Users VALUES (:code, :f_name, :l_name, :email, :status)",
                               {
                                   'code': code,
                                   'f_name': first_name,
                                   'l_name': last_name,
                                   'email': email,
                                   'status': status
                               })
                connection.commit()
                filename = str(first_name + last_name + ".jpg")
                make_qr(code, filename)
            except sqlite3.Error as er:
                handle_sqlite_error(er)

    def login(self, timestamp: str, userCode: str) -> None:
        """Add a record to the Logins table for a user login.

        Args:
            timestamp (str): The timestamp of the login.
            userCode (str): The user code of the user logging in.

        Returns:
            None
        """
        # Use a context manager (with statement) for the connection
        with self.connect() as connection:
            cursor = connection.cursor()
            # Insert into table and commit the changes
            try:
                cursor.execute("INSERT INTO Logins(timestamp, userCode) VALUES (:timestamp, :userCode)",
                               {
                                   'timestamp': timestamp,
                                   'userCode': userCode
                               })
                connection.commit()
            except sqlite3.Error as er:
                handle_sqlite_error(er)

    def logout(self, userCode: str, logoutTime: str) -> None:
        """Update the logout time for the entry in the Logins table with the given user code.

        Args:
            userCode (str): The user code of the user logging out.
            logoutTime (str): The timestamp of the logout.

        Returns:
            None
        """
        # Use a context manager (with statement) for the connection
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""UPDATE Logins SET logoutTime = ? WHERE userCode = ? AND logoutTime IS NULL""",
                               (logoutTime, userCode))
                connection.commit()
            except sqlite3.Error as er:
                handle_sqlite_error(er)

    def get_info(self, code: str) -> Optional[Tuple[str, str, str, str, Optional[str]]]:
        """Get the record for the user with the given code and return its values.

        Args:
            code (str): The user code to look up.

        Returns:
            Tuple[str, str, str, str, Optional[str]]: A tuple containing the user information
                (code, first name, last name, email, and status if available) or None if not found.
        """
        # Use a context manager (with statement) for the connection
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT * FROM Users WHERE code=?", (code,))
                user = cursor.fetchone()
                return user
            except sqlite3.Error as er:
                handle_sqlite_error(er)

    def get_whitelist(self) -> np.ndarray:
        """Get all codes from the Users table and return as a list of authorized codes.

        Returns:
            np.ndarray: An array of authorized codes for logging in/out of the system.
        """
        # Use a context manager (with statement) for the connection
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT code FROM Users")
                codes = cursor.fetchall()
                codes = np.array(codes)
                whitelist = codes[:, 0]
                return whitelist
            except sqlite3.Error as er:
                handle_sqlite_error(er)

    def set_status(self, code: str) -> str:
        """Get the status for the user with the given code and update its value accordingly.

        Args:
            code (str): The user code to set the status for.

        Returns:
            str: The updated status of the user ("Active" or "Inactive").
        """
        # Use a context manager (with statement) for the connection
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                user = self.get_info(code)
                if user[4] == 'Inactive' or user[4] is None:
                    print("User's status is inactive or none - setting to active")
                    cursor.execute("UPDATE Users SET status='Active' WHERE code=?", (code,))
                    connection.commit()
                    status = 'Active'
                    return status
                elif user[4] == 'Active':
                    print("User's status is active - setting to Inactive")
                    cursor.execute("UPDATE Users SET status='Inactive' WHERE code=?", (code,))
                    connection.commit()
                    status = 'Inactive'
                    return status
                else:
                    print("Code Could not be recognized")
            except sqlite3.Error as er:
                handle_sqlite_error(er)

