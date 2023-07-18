"""
Author: Jacob Pitsenberger
Program: main.py
Version: 1.0
Project: QR Code Login System
Date: 7/18/2023
Purpose: This program contains the main method for running the QR Code Login System
Uses: qr_db_logger.py
"""

from qr_db_logger import QrLogger


def main():
    """Main method to run the QR Code Login System.

    Returns:
        None
    """
    qrLogger = QrLogger()
    qrLogger.run()


if __name__ == "__main__":
    main()
