# Patient Information Management System

A data management system designed to facilitate the processing of patient information. This project is built using Django and operates within an SQLite environment.

**Note**: This project is an adapted version, and all rights belong to the original developer, Sumit Kumar. It is utilized solely for educational purposes. All credits go to the original developer.

## Features Added:

- Date & Scheduling Appointment (Staff-Admin)
- Authentication for Staff, Doctor, and Patients

## Bug Fixes and Improvements:

- Clickable cards instead of plain text.

## Planning to Add:

- Email Verification (Both Login & Register)
- Chat Plugin integration from Messenger
- Appointment Notifications on both Doctor and Patient Emails
- Message Notifications

## Setting Up and Running the Local Server:

1. Set up a virtual environment:

    ```bash
    python -m venv venv
    ```

2. Set the execution policy for the current PowerShell session to RemoteSigned:

    ```bash
    Set-ExecutionPolicy RemoteSigned -Scope Process
    ```

3. Activate the virtual environment:

    ```bash
    venv/Scripts/activate
    ```

4. Install dependencies, apply migrations, and run the local server:

    ```bash
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    ```

### Superuser Access to Django Database:

To create a superuser and access the Django admin site:

```bash
python manage.py createsuperuser
```

**Note**: Original Project: [Hospital Management System Django](https://github.com/sumitkumar1503/hospitalmanagement) by Sumit Kumar. This project uses Python with the Django Web Framework, SQLite as the database, and is developed as a web application.
