# QR Code Login System

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Authors](#authors)
- [License](#license)

## Introduction

The QR Code Login System is a Python-based application designed to log users in and out of a system using QR codes. The system captures QR codes containing users' personal access codes and records their login or logout activities, along with timestamps, by saving images with relevant information.

The primary purpose of this project is to provide a simple and secure login mechanism using QR codes, which can be easily scanned by users to access a system. This project can be used in various scenarios where quick and convenient login is required.

## Features

- QR code-based login and logout mechanism.
- Real-time logging and notification of user activities.
- Database integration to store user information and login/logout timestamps.
- QR code generation for user access codes.

## Requirements

- Python 3.x
- OpenCV (cv2) library
- pyzbar library
- NumPy library
- qrcode library
- SQLite3 library (included with Python)

## Installation

1. Clone the repository or download the source code: git clone https://github.com/your-username/qr-code-login-system.git
cd qr-code-login-system
2. Install the required dependencies using pip: pip install opencv-python pyzbar numpy qrcode
3. Run the application: python main.py

## Usage

1. Ensure that the camera is properly connected to the system.

2. Run the `main.py` script to start the QR Code Login System.

3. Display a user's unique access code as a QR code on their device.

4. Use the system to scan the QR code. The system will detect the code, log the user in, and display the user's information.

5. To log out, display the same QR code again. The system will recognize the code and log the user out.

## Authors

- [Jacob Pitsenberger](https://github.com/Jacob-Pitsenberger)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

