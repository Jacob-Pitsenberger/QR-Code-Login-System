import unittest
import cv2
import numpy as np
from qr_db_logger import QrLogger
from users_dao import Users, make_qr
import os


class TestQrDbLogger(unittest.TestCase):
    def setUp(self):
        self.logger = QrLogger()
        self.users = Users()
        self.user_code_1 = 'h65ld310'
        self.user_code_2 = 'd08ae169'

    def test_process_qr_with_known_qr(self):
        # Simulate a frame and get its height.
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_height = frame.shape[0]

        # Make a qr code with data for user_code_1 and read it as an image.
        make_qr(self.user_code_1, 'temp.jpg')
        qr_code = cv2.imread('../data/qr_images/temp.jpg')
        os.remove('../data/qr_images/temp.jpg')

        # Resize the qr_code image to match the height of the simulated frame.
        qr_code = cv2.resize(qr_code, (qr_code.shape[1], frame_height))

        # Concatenate the frame and qr_code images horizontally
        frame = np.concatenate((frame, qr_code), axis=1)

        # Pass the concatenated frame to the process_qr method.
        info = self.logger.process_qr(frame, [])

        # Should be a qr code in the info list.
        if len(info) > 1:
            # If there is a qr code info should also contain the data and timestamp so 3 elements.
            self.assertEqual(len(info), 3)
            # First element should be the frame
            self.assertIs(info[0], frame)
            # Second element should be the users code found from decoding the qr_code image in the frame.
            self.assertEqual(info[1].decode(), self.user_code_1)
            # There should also be a timestamp value associated with the instance.
            self.assertIsInstance(info[2], float)
        else:
            # There is no qr code so frame is only element in list.
            self.assertEqual(len(info), 1)

    def test_process_qr_with_unknown_qr(self):
        # Simulate a frame and get its height.
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame_height = frame.shape[0]

        # Make a qr code with data for a code not associated with a user and read it as an image.
        make_qr('unknownQR', 'temp.jpg')
        qr_code = cv2.imread('../data/qr_images/temp.jpg')
        os.remove('../data/qr_images/temp.jpg')

        # Resize the qr_code image to match the height of the simulated frame.
        qr_code = cv2.resize(qr_code, (qr_code.shape[1], frame_height))

        # Concatenate the frame and qr_code images horizontally
        frame = np.concatenate((frame, qr_code), axis=1)

        # Pass the concatenated frame to the process_qr method.
        info = self.logger.process_qr(frame, [])
        # If a qr code is not recognized then only the frame is returned so only one element should be in the list.
        self.assertIs(len(info), 1)
        # The frame should be in the list.
        self.assertIs(info[0], frame)

    def tearDown(self):
        # Clean up any test files created
        os.remove('../data/qr_images/JohnBuck.jpg')
        os.remove('../data/qr_images/JaneDoe.jpg')
        # os.remove('data/test_user_database.db')
