
---

# Image Analysis & Comparison Web App

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.x-black.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green.svg)
![Azure](https://img.shields.io/badge/Azure%20Cognitive%20Services-Vision-blue)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A full-stack web application built with Flask that allows users to register, upload images, and perform advanced analysis and comparison using **Azure Cognitive Services for Vision**. User data and images are securely stored in a **MongoDB Atlas** database.

## Table of Contents

- [Key Features](#key-features)
- [Live Demo](#live-demo)
- [Technology Stack](#technology-stack)
- [Screenshots](#screenshots)
- [Setup and Installation](#setup-and-installation)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Code Overview](#code-overview)
- [Contributing](#contributing)
- [License](#license)

## Key Features

-   **User Authentication**: Secure user registration and login system with password hashing (`bcrypt`).
-   **Persistent Sessions**: Manages user sessions with `Flask-Login`.
-   **User Profiles**: Each user has a profile page displaying their personal information and uploaded images.
-   **Image Upload & Storage**: Users can upload images, which are stored as Base64 strings in their MongoDB user document.
-   **Cloud-Powered Image Analysis**: Leverages **Azure Computer Vision API** to analyze uploaded images and extract:
    -   A human-readable description (caption).
    -   Relevant tags with confidence scores.
    -   Identified categories.
    -   Detected objects within the image.
-   **Intelligent Image Comparison**:
    -   Analyzes two user-provided images.
    -   Compares them based on their generated tags and descriptions.
    -   Calculates a similarity percentage based on common tags.
    -   Highlights key differences between the images.

## Live Demo

[Link to your deployed application (if available)]

## Technology Stack

-   **Backend**: Python, Flask
-   **Database**: MongoDB (with MongoDB Atlas for cloud hosting)
-   **Cloud Service**: Microsoft Azure Cognitive Services (Computer Vision)
-   **Authentication**: Flask-Login, bcrypt
-   **Frontend**: HTML, Jinja2 Templating
-   **Environment Management**: python-dotenv

## Screenshots

*(Here you can add screenshots of your application to give a visual overview.)*

**Example Placeholders:**

| Login Page | User Profile | Analysis Result |
| :---: | :---: | :---: |
| *[Image of login.html]* | *[Image of profile.html with uploaded images]* | *[Image of result.html with analysis data]* |

## Setup and Installation

Follow these steps to get the application running on your local machine.

### Prerequisites

-   Python 3.8+
-   Git
-   A **MongoDB Atlas** account and a cluster.
-   A **Microsoft Azure** account with a Computer Vision resource created.

### Installation Steps

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  **Create and activate a virtual environment:**
    <details>
    <summary>For macOS/Linux</summary>

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```
    </details>
    <details>
    <summary>For Windows</summary>

    ```sh
    python -m venv venv
    venv\Scripts\activate
    ```
    </details>

3.  **Install the required dependencies:**
    Create a `requirements.txt` file in the root directory with the following content:
    ```
    Flask
    Flask-Login
    pymongo[srv]
    bcrypt
    python-dotenv
    azure-cognitiveservices-vision-computervision
    msrestazure
    ```
    Then, run the installation command:
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root of the project directory. Populate it with your credentials. **Do not commit this file to version control.**

    ```dotenv
    # .env file

    # Flask secret key for session management
    SECRET_KEY='your_super_secret_key_here'

    # Azure Computer Vision Credentials
    AZURE_COMPUTER_VISION_KEY='your_azure_vision_api_key'
    AZURE_COMPUTER_VISION_ENDPOINT='your_azure_vision_endpoint_url'
    ```
    **Note**: The MongoDB URI in the provided `app.py` is hardcoded. It is a security risk to commit credentials. For best practice, you should move it from the code to this `.env` file and load it using `os.getenv()`.

5.  **Run the Flask application:**
    ```sh
    flask run
    ```
    The application will be running at `http://127.0.0.1:5000`.

## Usage

1.  Navigate to `http://127.0.0.1:5000`.
2.  **Register** for a new account or **Login** if you already have one.
3.  After logging in, you will be redirected to your **Profile** page.
4.  Use the **Upload Image** form to add images to your profile. Your uploaded images will appear as thumbnails.
5.  Click the **"Analyze"** button below any image to see a detailed analysis from the Azure Vision API.
6.  To compare two new images, use the **"Compare Images"** form on your profile page.

## API Endpoints

| Method | Endpoint                    | Authentication | Description                                             |
| :----- | :-------------------------- | :------------- | :------------------------------------------------------ |
| `GET`  | `/`                         | Optional       | Renders the home page.                                  |
| `GET/POST`| `/register`                 | No             | Renders the registration page and handles user creation.|
| `GET/POST`| `/login`                    | No             | Renders the login page and handles user authentication. |
| `GET`  | `/logout`                   | Yes            | Logs out the current user.                              |
| `GET`  | `/profile`                  | Yes            | Displays the user's profile and uploaded images.        |
| `POST` | `/upload`                   | Yes            | Handles image uploads and saves them to the database.   |
| `GET`  | `/analyze/<int:image_index>`| Yes            | Analyzes a specific image and displays the results.     |
| `POST` | `/compare`                  | Yes            | Compares two newly uploaded images.                     |

## Code Overview

-   **`app.py`**: The main application file containing all the logic.
    -   **Initialization**: Sets up the Flask app, Flask-Login, MongoDB client, and Azure Vision client.
    -   **`User` Class**: A `UserMixin` model for handling user objects, including static methods for creating, finding, and loading users from MongoDB.
    -   **Routes**: Defines all the web page endpoints (`/`, `/login`, `/profile`, etc.) and their corresponding logic.
    -   **Helper Functions**:
        -   `analyze_image()`: Takes image data, sends it to the Azure API, and formats the JSON response.
        -   `compare_images()`: Orchestrates the comparison by calling `analyze_image()` for two images and then calculating their similarity and differences.

-   **`templates/`**: A directory containing all the HTML files for the frontend, using Jinja2 for dynamic content rendering.
    -   `index.html`: The public home page.
    -   `register.html` / `login.html`: Forms for user authentication.
    -   `profile.html`: The user's dashboard for uploading and viewing images.
    -   `result.html`: A generic template to display the results of either an analysis or a comparison.

-   **`.env`**: A file (not in version control) to store sensitive keys and configuration variables.

## Contributing

Contributions are welcome! If you have suggestions for improvements, please follow these steps:

1.  Fork the Project.
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the Branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

