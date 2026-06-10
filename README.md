# core

Django project with Django REST Framework automatically generated.

## Installation

1. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

2. Install dependencies (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env` (already done during setup)
   - Update `.env` with your specific settings if needed

## Running

```bash
python manage.py runserver
```

## API Endpoints

- Admin: http://127.0.0.1:8000/admin/
- API Root: http://127.0.0.1:8000/api/
- Hello API: http://127.0.0.1:8000/api/hello/
- Status Check: http://127.0.0.1:8000/api/hello/status/

## Structure

- `core/` - Main settings
- `api/` - Sample app with API
- `venv/` - Virtual environment
- `.env` - Environment variables (SECRET_KEY, DEBUG, etc.)
- `.env.example` - Template for environment variables
- `manage.py` - Django management script

## Development

To create a superuser:
```bash
python manage.py createsuperuser
```

To create a new app:
```bash
python manage.py startapp app_name
```

## Environment Variables

The project uses python-dotenv to load environment variables from `.env` file:
- `SECRET_KEY` - Django secret key (auto-generated)
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

Add more variables as needed for your project.
