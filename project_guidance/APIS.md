# API Endpoints & Authentication

## Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health Check / Welcome Message |
| `POST` | `/api/v1/auth/signup/` | Register a new user |
| `POST` | `/api/v1/auth/login/` | Login and obtain JWT tokens |
| `POST` | `/api/v1/auth/google/` | Login with Google token and obtain JWTs |
| `POST` | `/api/v1/auth/logout/` | Logout (Block refresh token) |
| `POST` | `/api/v1/auth/token/refresh/` | Refresh access token |
| `POST` | `/api/v1/auth/change-password/` | Change password (authenticated) |
| `POST` | `/api/v1/auth/password-reset/` | Request password reset link |
| `POST` | `/api/v1/auth/password-reset-confirm/` | Confirm password reset |
