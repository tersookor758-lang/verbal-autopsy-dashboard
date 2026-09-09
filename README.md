# Verbal Autopsy Outcome Dashboard

A secure, professional web application for managing, analyzing, validating, and visualizing Verbal Autopsy records across Nigeria.

The platform transforms Verbal Autopsy records into useful health-data intelligence through structured data management, analytics, visualization, reporting, and a secure REST API.

---

## Project Overview

The Verbal Autopsy Outcome Dashboard provides authorized users with a centralized platform for:

- Managing Verbal Autopsy records
- Searching and filtering health records
- Viewing dashboard statistics
- Visualizing health-data trends
- Uploading validated datasets
- Exporting records
- Managing user accounts
- Controlling permissions through role-based access control
- Accessing a documented REST API
- Managing data through a MySQL database

---

## Core Features

### Authentication

- User registration
- User login
- User logout
- Secure password hashing
- Session-based authentication
- JWT authentication for the REST API
- Access and refresh tokens
- Refresh-token rotation
- Account activation and verification
- Failed-login protection

### Role-Based Access Control

The application supports three primary roles.

#### User

Can:

- Access the dashboard
- View records
- Search and filter records
- Download/export records

Cannot:

- Upload datasets
- Modify records
- Delete records
- Manage users

#### Upload User

Can:

- Access the dashboard
- View records
- Search and filter records
- Download/export records
- Upload datasets

Upload functionality is restricted to authorized upload users.

#### Administrator

Can:

- Access the dashboard
- View records
- Search and filter records
- Upload datasets
- Export records
- Modify records
- Delete records
- Manage user accounts
- Approve accounts
- Activate accounts
- Deactivate accounts
- Change user roles

### Super Administrator

The built-in account with username:

```text
admin