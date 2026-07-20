# Verbal Autopsy Outcome Dashboard

A Flask-based web application for managing, analyzing, validating, and visualizing Verbal Autopsy records across Nigeria.

---

## Features

- Dashboard with summary statistics
- Interactive charts using Chart.js
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
- Automatic validation and normalization
- Export records to:
  - CSV
  - Excel
  - JSON
- REST API with Swagger documentation
- SQLite database
- Responsive Bootstrap interface

---

## Technologies Used

- Python
- Flask
- Flask-RESTX
- Flask-SQLAlchemy
- Bootstrap 5
- Chart.js
- Pandas
- OpenPyXL
- SQLite

---

## Project Structure

```text
project/
│
├── api/
├── dashboard/
├── resources/
│   ├── raw/
│   └── utils/
├── static/
│   ├── css/
│   └── js/
├── templates/
├── uploads/
├── app.py
├── config.py
├── models.py
├── extensions.py
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
```

Move into the project:

```bash
cd project
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment.

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

The application will start at:

```text
http://127.0.0.1:5000
```

---

## API Documentation

Swagger UI is available at:

```text
http://127.0.0.1:5000/api/
```

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

## Dashboard Features

- Summary statistics
- Interactive charts
- Pagination
- Dynamic State → LGA filtering
- Search and filtering
- Data upload
- Data export

---

## License

This project is provided for educational and research purposes.