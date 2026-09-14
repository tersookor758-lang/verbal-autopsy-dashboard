# Verbal Autopsy Outcome Dashboard

A secure, professional web application for managing, validating, analyzing, and visualizing Verbal Autopsy records across Nigeria.

The platform transforms Verbal Autopsy records into useful health-data intelligence through structured data management, analytics, visualization, reporting, and a secure REST API.

---

## Project Overview

The Verbal Autopsy Outcome Dashboard provides authorized users with a centralized platform for:

* Managing Verbal Autopsy records
* Searching and filtering health records
* Viewing dashboard statistics
* Visualizing health-data trends
* Uploading validated datasets
* Exporting records
* Managing user accounts
* Controlling permissions through role-based access control
* Accessing a documented REST API
* Managing data through a MySQL database

---

## Core Features

### Authentication

* User registration, login, and logout
* Secure password hashing
* Session-based authentication
* JWT authentication for REST API access
* Access and refresh token management
* Refresh-token revocation
* Failed-login protection
* Account activation and deactivation
* Role-based access control
* Protected Super Administrator account

### Dashboard

* Summary statistics
* Interactive data visualization using Chart.js
* Search functionality
* Pagination
* Advanced filtering by:

  * State
  * LGA
  * Facility
  * Cause of Death
  * Interview Year
  * Patient ID

### Data Management

* Upload Verbal Autopsy datasets
* Supported upload formats:

  * CSV
  * Excel (`.xlsx`)
  * Excel (`.xls`)
  * JSON
* Automatic validation and normalization of uploaded records
* Authorized record management
* Data export to:

  * CSV
  * Excel
  * JSON

### API

* REST API built with Flask-RESTX
* Swagger API documentation
* JWT-protected API endpoints
* Access and refresh token management
* API authentication and authorization

### Security

* Password hashing
* Session-based authentication
* JWT authentication
* Role-based authorization
* Refresh-token revocation
* CSRF protection for browser forms
* Rate limiting
* Secure production session-cookie configuration
* Environment-based secrets
* Explicit production CORS configuration
* Production configuration validation

### Database

* MySQL support
* SQLAlchemy ORM
* Flask-Migrate/Alembic migrations
* Database connectivity health checks

---

## User Roles

### User

Regular users can:

* Access the dashboard
* View records
* Search and filter records
* Download/export records

Regular users cannot:

* Upload datasets
* Modify records
* Delete records
* Manage users

### Upload User

Upload Users have all regular-user permissions and can additionally:

* Upload Verbal Autopsy datasets

### Administrator

Administrators can:

* Access the dashboard
* View records
* Search and filter records
* Upload datasets
* Export records
* Modify records
* Delete records
* Manage user accounts
* Activate and deactivate accounts
* Change user roles
* Perform other authorized administrative operations

### Super Administrator

The built-in account with username:

```text
admin
```

is the permanent Super Administrator.

The Super Administrator cannot be:

* Demoted
* Deactivated
* Deleted
* Replaced by another administrator

New accounts are automatically created as regular users. Higher permissions must be granted by an authorized administrator.

---

## Technologies Used

* Python
* Flask
* Flask-RESTX
* Flask-SQLAlchemy
* Flask-Migrate
* Alembic
* MySQL
* PyMySQL
* Flask-Login
* Flask-JWT-Extended
* Flask-WTF
* Flask-Limiter
* Flask-CORS
* Pandas
* OpenPyXL
* Bootstrap 5
* Chart.js
* Gunicorn

---

## Project Structure

```text
project/
│
├── Auth/
├── admin/
├── api/
├── dashboard/
├── migrations/
│   └── versions/
├── resources/
├── static/
├── templates/
├── app.py
├── config.py
├── extensions.py
├── models.py
├── init_db.py
├── requirements.txt
├── runtime.txt
├── wsgi.py
└── README.md
```

---

## Local Development

Create a virtual environment:

```text
python -m venv venv
```

Activate it.

### Windows

```text
venv\Scripts\activate
```

### Linux/macOS

```text
source venv/bin/activate
```

Install dependencies:

```text
pip install -r requirements.txt
```

Configure the required environment variables for the selected development configuration.

Run the application:

```text
python app.py
```

The host and port are determined by the application's development configuration.

---

## Database Migrations

Database schema changes are managed with Flask-Migrate and Alembic.

Do not use `db.create_all()` as a production schema-management mechanism.

Apply migrations with:

```text
flask db upgrade
```

Before deployment, verify the migrations against the target MySQL database and confirm that the schema matches the application's models.

The database connection can be checked with:

```text
python init_db.py
```

`init_db.py` verifies production database connectivity and does not create the production schema.

---

## Production Configuration

Production requires environment variables for application secrets, database connectivity, rate-limit storage, and allowed CORS origins.

At minimum, configure:

```text
APP_ENV=production

SECRET_KEY=<strong-random-secret>

JWT_SECRET_KEY=<strong-random-secret>

USE_MYSQL=true

DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:3306/<database>

RATE_LIMIT_STORAGE_URI=<production-rate-limit-storage>

CORS_ORIGINS=<allowed-frontend-origin>
```

Do not commit `.env` files or production secrets to source control.

The application validates required production configuration during startup.

---

## Production Server

The repository includes `wsgi.py` for WSGI-compatible deployment platforms.

A typical Gunicorn command is:

```text
gunicorn wsgi:app
```

The deployment environment should provide:

* Production environment variables
* A persistent MySQL database
* Persistent rate-limit storage where required

---

## API Documentation

Swagger UI is available at:

```text
/api/swagger
```

The REST API is exposed under the:

```text
/api
```

namespace.

Protected API endpoints require JWT authentication. After authenticating through the API login endpoint, the returned JWT can be supplied as a Bearer token through Swagger's authorization controls.

---

## Health Check

The application exposes:

```text
/health
```

The health-check endpoint verifies application and database connectivity and reports the current health status.

---

## Supported Upload Formats

* CSV
* Excel (`.xlsx`)
* Excel (`.xls`)
* JSON

---

## Supported Export Formats

* CSV
* Excel
* JSON

---

## Security Controls

The application includes:

* Password hashing
* Session-based authentication
* JWT authentication
* Refresh-token revocation
* Role-based authorization
* Super Administrator protection
* CSRF protection
* Rate limiting
* Secure production session cookies
* Production secret validation
* Explicit CORS configuration
* Environment-based configuration
* Database health checks

---

## Deployment Checklist

Before production deployment:

1. Configure `APP_ENV=production`.
2. Set strong production `SECRET_KEY` and `JWT_SECRET_KEY` values.
3. Configure the production MySQL `DATABASE_URL`.
4. Set `USE_MYSQL=true`.
5. Configure persistent `RATE_LIMIT_STORAGE_URI`.
6. Set explicit `CORS_ORIGINS` values.
7. Install the pinned dependencies from `requirements.txt`.
8. Run `flask db upgrade` against the intended database.
9. Verify `/health` after deployment.
10. Verify `/api/swagger` and protected API authentication.
11. Test login, signup, role-based access, uploads, exports, and administrator controls.
12. Confirm the Super Administrator account cannot be modified or removed by another administrator.
13. Confirm `.env` files and production secrets are not committed to source control.
14. Perform a final end-to-end regression test after deployment.

---

## Project Status

The Verbal Autopsy Outcome Dashboard has reached the **final deployment-readiness and project handover phase**.

Core application development, authentication, role-based access control, database integration, dashboard functionality, analytics, reporting, API functionality, and security controls have been implemented.

The remaining activities are focused on:

* Final code cleanup
* Regression testing
* Migration validation
* Production configuration verification
* Deployment
* Post-deployment testing
* Documentation and project handover

---

## License

This project is provided for educational and research purposes.
