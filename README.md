
# AI-Powered-Security-System Server

This is the server-side application of the AI-Powered  Security System, built with Flask. It processes images sent from the client-side application upon motion detection and performs intelligent image analysis to enhance security.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Description

The server-side application of the AI-Powered Security System receives images from the client-side application when motion is detected. It performs analysis to detect humans, animals, or unidentified objects using gemini api and sends alerts via email and SMS.

## Features

- Image processing and analysis
- Intelligent detection of humans, animals, or unidentified objects
- Email and SMS alert generation

## Installation

To get started with the server-side application, follow these steps:

### Prerequisites

Make sure you have the following installed on your system:

- Python 3.7 or higher
- pip (Python package installer)

### Clone the Repository

Clone the repository to your local machine using the following command:

```bash
git clone https://github.com/AI-Varun/AI-Powered-Security-System-Server.git
```
### Install Dependencies
Navigate to the project directory and install the required dependencies:

```bash
pip install -r requirements.txt
```
### Usage
To run the application locally, use the following command:
```bash
python app.py
```

This will start the Flask development server. The application will be accessible at http://127.0.0.1:6754.

### API Endpoint
/upload (POST): Endpoint to receive images for analysis from the client-side application.

### Motion Detection and Image Capture
* The application will use the camera to monitor for motion.
* When motion is detected, an image will be captured and sent to the backend server automatically.


### Contributing
Contributions are welcome! To contribute to this project, follow these steps:

* Fork the repository.
* Create a new branch (git checkout -b feature-branch).
* Make your changes.
* Commit your changes (git commit -m 'Add some feature').
* Push to the branch (git push origin feature-branch).
* Open a Pull Request.
