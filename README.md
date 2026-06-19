# KanMind Backend

Django REST Framework backend for the KanMind Kanban board application. This API provides user authentication, board management, and task tracking functionality.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

Follow these steps to set up the project locally:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment

Linux/Mac:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and update it with your settings:

```bash
cp .env.example .env
```

Edit `.env` and update the following variables:
- `SECRET_KEY` - Django secret key (generate a new one for production)
- `DEBUG` - Set to `True` for development, `False` for production
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

To generate a new secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)

To access the Django admin panel:

```bash
python manage.py createsuperuser
```

## Running the Application

Start the development server:

```bash
python manage.py runserver
```

The API will be available at: http://127.0.0.1:8000/

## API Endpoints

### Authentication
- `POST /api/registration/` - User registration
- `POST /api/login/` - User login

### Boards
- `GET /api/boards/` - List all boards
- `POST /api/boards/` - Create a new board
- `GET /api/boards/<id>/` - Get board details
- `PUT /api/boards/<id>/` - Update board
- `DELETE /api/boards/<id>/` - Delete board
- `POST /api/email-check/` - Check if email exists

### Tasks
- `POST /api/tasks/` - Create a new task
- `GET /api/tasks/assigned-to-me/` - Get tasks assigned to current user
- `GET /api/tasks/reviewing/` - Get tasks for review
- `GET /api/tasks/<id>/` - Get task details
- `PUT /api/tasks/<id>/` - Update task
- `DELETE /api/tasks/<id>/` - Delete task
- `GET /api/tasks/<id>/comments/` - List task comments
- `POST /api/tasks/<id>/comments/` - Add comment to task
- `DELETE /api/tasks/<id>/comments/<comment_id>/` - Delete comment

### Admin Panel
- `GET /admin/` - Django admin interface

## Project Structure

```
KanMind-Backend/
├── auth_app/           # User authentication and registration
├── boards_app/         # Board management
├── tasks_app/          # Task and comment management
├── core/               # Project settings and configuration
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not in git)
├── .env.example        # Environment variables template
└── db.sqlite3          # SQLite database (created after migrations)
```

## Development Commands

### Create a new app
```bash
python manage.py startapp app_name
```

### Make migrations after model changes
```bash
python manage.py makemigrations
python manage.py migrate
```

### Run tests
```bash
python manage.py test
```

### Collect static files
```bash
python manage.py collectstatic
```

## Technology Stack

- Django 6.0.6
- Django REST Framework 3.17.1
- Django CORS Headers 4.9.0
- Python Dotenv 1.2.2
- SQLite (default database)

## Notes

- This is a development server. Do not use it in production.
- For production deployment, use a proper WSGI/ASGI server like Gunicorn or uWSGI.
- Change `DEBUG=False` and set proper `ALLOWED_HOSTS` in production.
- Consider using PostgreSQL or MySQL for production instead of SQLite.
- The default CORS settings allow all origins for development. Restrict this in production.
