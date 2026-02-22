# Project Structure

The project is structured into distinct applications and configurations to keep concerns separated.

```text
smart_guide_be/
├── apps/                # Django apps representing main business domains
│   └── users/           # User management app (models, api views, routes)
├── common/              # Shared utilities, permissions, and helpers
├── config/              # Project level configuration
│   ├── settings/        # Django settings and environment variables
│   ├── urls.py          # Main URL routing definitions
│   ├── asgi.py          # ASGI interface (for async apps/websockets)
│   └── wsgi.py          # WSGI interface (for deployment)
├── .env                 # Environment variables file (not tracked in git)
├── manage.py            # Django management script for CLI operations
├── requirements.txt     # Python dependencies tracking
├── SETUP.md             # Documentation for setting up the project locally
├── APIS.md              # Documentation for API endpoints and Google Auth
└── README.md            # Project entrypoint documentation
```
