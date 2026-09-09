# Verbal Autopsy Outcome Dashboard

A Flask-based web application for managing, validating, analyzing, and visualizing Verbal Autopsy records across Nigeria.

The application is designed as a secure, role-based health-data dashboard with MySQL support, REST APIs, Swagger documentation, reporting/export tools, and production deployment support.

---

## Core Features

- Public landing page
- User registration, login, and logout
- Role-based access control
- Automatic regular-user account creation on signup
- Administrator-controlled role upgrades
- User account activation/deactivation and management
- Protected Super Administrator account
- Dashboard with summary statistics
- Interactive charts using Chart.js
- Search, filtering, and pagination
- Filter records by:
  - State
  - LGA
  - Facility
  - Cause of Death
  - Interview Year
  - Patient ID
- Upload records from:
  - CSV
  - Excel (.xlsx/.xls)
  - JSON
- Automatic validation and normalization of uploaded records
- Export records to:
  - CSV
  - Excel
  - JSON
- REST API with Swagger UI
- JWT authentication for API access
- Refresh-token management and revocation
- CSRF protection for browser forms
- Rate limiting
- Production configuration validation
- MySQL database support
- Flask-Migrate/Alembic database migrations
- Health-check endpoint
- Responsive Bootstrap interface

---

## User Roles

### User

- Access the dashboard
- Search and filter records
- Download/export records

### Upload User

- Everything available to a regular user
- Upload verbal autopsy records

### Admin

- Full dashboard access
- Upload and data-management permissions
- User management
- Account activation/deactivation
- Role management
- Other administrative controls

The built-in `admin` account is the permanent Super Administrator. It cannot be demoted, deactivated, deleted, or replaced by another account.

---

## Technologies Used

- Python
- Flask
- Flask-RESTX
- Flask-SQLAlchemy
- Flask-Migrate / Alembic
- MySQL
- PyMySQL
- Flask-Login
- Flask-JWT-Extended
- Flask-WTF
- Flask-Limiter
- Flask-CORS
- Pandas
- OpenPyXL
- Bootstrap 5
- Chart.js
- Gunicorn

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

Windows:

```text
venv\Scripts\activate
```

Linux/macOS:

```text
source venv/bin/activate
```

Install dependencies:

```text
pip install -r requirements.txt
```

For local development, the application can use its development configuration and local SQLite database. Production deployments must use MySQL.

Run the application:

```text
python app.py
```

The exact host and port are determined by the application's development configuration.

---

## Database Migrations

Database schema changes are managed with Flask-Migrate/Alembic.

Do not use `db.create_all()` as a production schema-management mechanism.

Apply migrations with:

```text
flask db upgrade
```

Before deploying, verify the migration against the target MySQL database and confirm that the schema matches the application's models.

The production database connection can also be checked with:

```text
python init_db.py
```

`init_db.py` verifies production database connectivity and deliberately does not create the production schema.

---

## Production Configuration

Production requires environment variables for secrets, the MySQL database, rate-limit storage, and allowed CORS origins.

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

The deployment platform should provide the production environment variables and a persistent MySQL database.

---

## API Documentation

Swagger UI is available under the API blueprint at:

```text
/api/swagger
```

The REST API is exposed under the `/api` namespace.

For protected API endpoints, authenticate through the API login endpoint and use the returned JWT as a Bearer token in Swagger's authorization controls.

---

## Health Check

The application exposes:

```text
/health
```

The endpoint checks database connectivity and reports the application's health status.

---

## Supported Upload Formats

- CSV
- Excel (.xlsx)
- Excel (.xls)
- JSON

---

## Supported Export Formats

- CSV
- Excel
- JSON

---

## Security Controls

The application includes:

- Password hashing
- Session-based authentication
- JWT authentication
- Refresh-token revocation
- Role-based authorization
- Super Administrator protection
- CSRF protection for browser forms
- Rate limiting
- Secure production session-cookie settings
- Production secret validation
- Explicit production CORS configuration
- Database connectivity health checks
- Environment-based configuration

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
12. Confirm that the Super Administrator account cannot be modified or removed by another administrator.
13. Confirm production secrets and `.env` files are not committed to the repository.

---

## Project Status

The project is in the final deployment-readiness phase: clean-up, regression testing, migration validation, production configuration verification, deployment, and post-deployment testing.

---

## License

This project is provided for educational and research purposes.
