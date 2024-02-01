# Patient Information Management System

A data management system that facilitates the processing of patient information. Developed using Django and SQLite environment.

**Note**: This project is an adapted version, and all rights belong to the original developer. It is utilized solely for educational purposes. All credits go to the original developer, Sumit Kumar.

## Features Added:

- Date & Scheduling Appointment (Staff-Admin)
- Authentication for Staffs, Doctor, and The Patient

## Bug Fixes and Improvements:

- Cards are now clickable instead of a text.

## Planning to Add:

- Email Verification (Both Login & Register)
- Chat Plugin from Messager
- Appointment Notification on Both Doctor and Patient Email
- Message Notification

## Setting Up and Running the Local Server:

Assuming you have VSCode, type the following commands in the terminal:

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

**Note**: Original Project: [Hospital Management System Django](https://github.com/sumitkumar1503/hospitalmanagement) by Sumit Kumar. The project uses Python with Django Web Framework, SQLite as the database, and is developed as a web application.
