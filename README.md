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

## Requirements and Installation Instructions

### 1. Python Installation:

Before proceeding, ensure that Python is installed on your system. If not, follow these steps:

#### For Windows:

1. Download the latest Python installer for Windows from [python.org](https://www.python.org/downloads/).

2. Run the installer and check the box that says "Add Python to PATH" during installation.

3. Verify the installation by opening a Command Prompt and running:

    ```bash
    python --version
    ```

#### For macOS:

1. macOS usually comes with Python pre-installed. Open Terminal and run:

    ```bash
    python3 --version
    ```

    If Python is not installed, you can install it using [Homebrew](https://brew.sh/):

    ```bash
    brew install python
    ```

#### For Linux (Ubuntu/Debian):

1. Open a terminal and run:

    ```bash
    sudo apt-get update
    sudo apt-get install python3
    ```

2. Verify the installation:

    ```bash
    python3 --version
    ```

### 2. Checking Python in PATH:

Ensure that Python is added to the system PATH. Open a new terminal/command prompt window and run:

```bash
python --version
```

If it returns the Python version, you're all set. If not, you may need to update your system PATH.

### 3. SQLite Installation:

SQLite comes bundled with Python, so there's usually no need for a separate installation.

### 4. SQLiteStudio:

You can use [SQLiteStudio](https://sqlitestudio.pl/) as a GUI tool for managing SQLite databases. Download and install it according to your operating system.

---

With these tools installed and Python in your system PATH, you can proceed with setting up the Patient Information Management System as described in the previous README section.

Note: Ensure that you have administrative privileges for installing Python and modifying the system PATH.

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
