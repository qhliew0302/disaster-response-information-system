# Disaster Response Information System (DRIS)

A web-based system designed to manage disaster response operations, including reporting incidents, requesting aid, managing shelters, and coordinating volunteers.

## Features

- Disaster reporting and tracking
- Aid request management
- Volunteer coordination and assignment
- Shelter management
- User authentication and role-based access
- Admin dashboard for oversight and management

## Prerequisites

- Python 3.8+
- Django 4.x
- SQLite (included with Django)

## Installation

1. Clone the repository or download the source code:

```bash
git clone https://github.com/qhliew0302/disaster-response-information-system.git
```

2. Set up a virtual environment (recommended):

```bash
python -m venv venv
```

3. Activate the virtual environment:

- On Windows:
```bash
venv\Scripts\activate
```

- On macOS/Linux:
```bash
source venv/bin/activate
```

4. Install Django:

```bash
pip install django
```

## Running the Application

1. Apply database migrations:

```bash
python manage.py migrate
```

2. Create a superuser (admin account):

```bash
python manage.py createsuperuser
```

3. Start the development server:

```bash
python manage.py runserver
```

4. Access the application in your web browser:
   - Main site: http://127.0.0.1:8000/
   - Admin interface: http://127.0.0.1:8000/admin/

## System Access

- **Admin Users (Authority)**: Full access to the admin dashboard and all system features
- **Volunteers**: Can view assignments and manage their profile
- **General Users (Citizen)**: Can report disasters, request aid, and view shelter information

