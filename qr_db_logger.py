"""
Author: Jacob Pitsenberger
Program: qr_db_logger.py
Version: 1.0
Project: QR Code Login System
Date: 7/18/2023
Purpose: This program is used to log users in and out of a system and notify them as such by saving
an image of when a qr code containing their personal access code is detected with the timestamp and
activity performed (login or logout) wrote on the image.
Uses: users_dao.py
"""

import time
from typing import List, Tuple
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from users_dao import Users
import os
from pathlib import Path

# Path to the log images directory
LOG_IMG_PATH = Path("data/log_images")

def make_log_dir() -> None:
    """Create the log images directory if it doesn't exist."""
    if not os.path.exists(LOG_IMG_PATH):
        LOG_IMG_PATH.mkdir()

class QrLogger:
    # Constants for validation messages and colors
    VALIDATION_MESSAGE_LOGIN = "Logged In"
    VALIDATION_MESSAGE_LOGOUT = "Logged Out"
    VALIDATION_COLOR_LOGIN = (0, 255, 0)  # Green
    VALIDATION_COLOR_LOGOUT = (0, 0, 255)  # Red
    CAMERA_DEVICE_ID = 0  # Camera ID
    WINDOW_X_POSITION = 100
    WINDOW_Y_POSITION = 100
    VALIDATION_DELAY_MS = 2500

    def __init__(self, log_img_path: Path = LOG_IMG_PATH):
        # Initialize the Users class.
        self.users = Users()

        self.log_img_path = log_img_path

        # Ensure the log images directory is made.
        make_log_dir()

        # Get the list of authorized users.
        self.authorized_users = self.users.get_whitelist()

    def process_qr(self, frame: np.ndarray, recent_accesses: List[str]) -> List:
        """Process QR codes in the frame and extract user information.

        Parameters:
            frame (np.ndarray): The frame containing the QR code.
            recent_accesses (List[str]): A list of recent user accesses.

        Returns:
            List: A list containing the frame, user code, and timestamp (if applicable).
        """
        try:
            # Decode any qr codes in the frame.
            qr_info = decode(frame)
            # Set the first element in info to the current frame.
            info = [frame]
            # if there is a qr code...
            if len(qr_info) > 0:
                # Should only be one qr code shown at a time so only one index.
                qr = qr_info[0]
                # Access the data.
                data = qr.data
                # If the data is an authorized user.
                if data.decode() in self.authorized_users:
                    # if there aren't any recent access or the last one wasn't for the current user.
                    if len(recent_accesses) == 0 or recent_accesses[-1] != data.decode():
                        # Update the latest access to be the current user.
                        recent_accesses.append(data.decode())
                        # Get the users code and the timestamp to return.
                        info.append(data)
                        info.append(time.time())
            # return the current frame and user code/timestamp if not the most recent access.
            return info
        except Exception as e:
            # In case of any exception during QR decoding, print the error and return the frame.
            print("Error while decoding QR code:", e)
            return info

    def log_qr_activity(self, info: List) -> np.ndarray:
        """Authorize the user based on the QR code information.

        Parameters:
            info (List): A list containing the frame, user code, and timestamp (if applicable).

        Returns:
            np.ndarray: The frame with validation information displayed.
        """
        # Get the frame for when the qr code is recognized
        frame = info[0]

        # If a user code and timestamp were returned.
        if len(info) > 1:
            # Get the access code and timestamp.
            code = info[1]
            timestamp = info[2]
            # Define the file name as the user code concatenated with the timestamp.
            filename = str(code) + " - " + str(timestamp) + ".jpg"
            # Define the path within the log images directory to save the image file.
            log_img = os.path.join(self.log_img_path, filename)
            # Set the Users Status according to their previous status (active or inactive).
            status = self.users.set_status(info[1].decode())
            # If status is active then the user is logging into the system.
            if status == "Active":
                # Write validation text on the qr log image stating logged in.
                self.show_validation(frame, info, self.VALIDATION_MESSAGE_LOGIN, self.VALIDATION_COLOR_LOGIN, log_img)
                # Log the user into the system.
                self.users.login(info[2], info[1].decode())
                print("User Logged into the system.")
            # If status isn't active then the user is logging out of the system.
            else:
                # Write validation text on the qr log image stating logged out.
                self.show_validation(frame, info, self.VALIDATION_MESSAGE_LOGOUT, self.VALIDATION_COLOR_LOGOUT, log_img)
                # Log the user out of the system.
                self.users.logout(info[1].decode(), info[2])
                print("User Logged out of the system.")
        # Return the most recent frame for video stream.
        return info[0]

    def show_validation(self, frame: np.ndarray, info: List, message: str, color: Tuple[int, int, int], log_img: str) -> None:
        """Display validation information on the frame.

        Parameters:
            frame (np.ndarray): The frame to display the validation information on.
            info (list): A list containing information to be displayed (frame, user code, timestamp).
            message (str): The message to be displayed on the frame.
            color (tuple): The color (BGR) to use for displaying the message.
            log_img (str): The filename to save the log image under.

        Returns:
            None
        """
        # Create a named window for the log image.
        cv2.namedWindow("Validation")
        # Resize the frame for the log image.
        frame = cv2.resize(frame, (480, 320))
        # Position the validation window right of the video stream window.
        cv2.moveWindow("Validation", 800, 200)
        # Put the validation message, user code, and timestamp on the log image.
        cv2.putText(frame, message, (75, 100), cv2.FONT_HERSHEY_COMPLEX, 1, color, 3)
        cv2.putText(frame, str(info[1]), (75, 150), cv2.FONT_HERSHEY_COMPLEX, 1, color, 3)
        cv2.putText(frame, str(info[2]), (75, 200), cv2.FONT_HERSHEY_COMPLEX, 1, color, 3)
        # Show the log image.
        cv2.imshow("Validation", frame)
        # Save the qr detected log image.
        cv2.imwrite(log_img, frame)
        # Wait a short delay so validation image can be verified.
        cv2.waitKey(self.VALIDATION_DELAY_MS)
        # Destroy the validation window to continue logging users in/out of the system.
        cv2.destroyWindow("Validation")

    def run(self) -> None:
        """Run the QR Code Login System.

        Returns:
            None
        """
        # Initialize a variable to hold a users code if they have been granted access already.
        recent_accesses = []

        # Create video capture object.
        cap = cv2.VideoCapture(self.CAMERA_DEVICE_ID)

        # Create a named window for the video stream.
        cv2.namedWindow("QR Code Login System")
        # Position the window.
        cv2.moveWindow("QR Code Login System", self.WINDOW_X_POSITION, self.WINDOW_Y_POSITION)

        while True:
            # Get the most recent frame.
            ret, frame = cap.read()

            # Show the recent accesses so that the user knows who has logged in and if another qr has been logged
            # since they logged in with theirs so that they can again use it to log out of the system.
            print("recent_accesses: " + str(recent_accesses))

            # Set the most recent frame to the return of the authorize_qr function when passing
            # the process_qr function as a parameter.
            frame = self.log_qr_activity(self.process_qr(frame, recent_accesses))

            # Show the video stream until a user presses 'q' or the program is terminated.
            cv2.imshow("QR Code Login System", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # Release the capture object and destroy the stream window to terminate the program.
        cap.release()
        cv2.destroyAllWindows()
