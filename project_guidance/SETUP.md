# Setup Instructions

## 1. Pull the Project
```bash
git clone <repository_url>
cd smart_guide_be
```

## 2. Activate Virtual Environment

**macOS/Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Install Requirements
```bash
pip install -r requirements.txt
```

## 4. Environment Configuration
Create a `.env` file in the root directory by copying the provided example file:

```bash
cp .env.example .env
```

Open the newly created `.env` file and fill in your actual database credentials, Django secret key, and Google OAuth credentials.

## 5. Run the Server
```bash
python manage.py migrate
python manage.py runserver
```

## Creating a Superuser
To access the Django Admin panel, you need to create a superuser:

```bash
python manage.py createsuperuser
```
Follow the prompts to set the email and password.

## Features
- **Custom User Model**: Uses `email` as the unique identifier instead of a username.
- **JWT Authentication**: Secure authentication using `rest_framework_simplejwt`.
- **Google Social Auth**: Complete integration with Google Sign-in to automatically handle user creation and JWT provisioning.

## Google Authentication Guide

To use Google Authentication, you need your own `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`. Here is how to set it up:

### 1. Get Google Credentials
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to your project (or create one).
3. Open the left navigation menu (hamburger icon) > **APIs & Services** > **Credentials**.
4. Click **+ CREATE CREDENTIALS** and select **OAuth client ID**.
   - **Application Type**: "Web application"
   - **Name**: "Postman Testing" (or your app name)
   - **Authorized redirect URIs**: Add `https://developers.google.com/oauthplayground` (for testing).
5. Copy the generated **Client ID** and **Client Secret** into your `.env` file.

### 2. Testing with Postman
Since you likely don't have a frontend yet, you can test the endpoint using Google's OAuth Playground:
1. Go to the [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/).
2. Click the gear icon (Top Right) > Check **"Use your own OAuth credentials"**.
3. Paste your Client ID and Client Secret, then Close.
4. On the left under "Step 1", scroll down to **Google OAuth2 API v2**, select the `userinfo.email` and `userinfo.profile` endpoints, and click **Authorize APIs**.
5. Once Authorized, click **Exchange authorization code for tokens** (Step 2).
6. Copy the `access_token` and make a POST request to your backend:
   - **URL:** `http://127.0.0.1:8000/api/v1/auth/google/`
   - **Body (JSON):** `{"access_token": "your-copied-token"}`
   - The response will contain your application's `access` and `refresh` JWTs!
