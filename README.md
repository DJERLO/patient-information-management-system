# Patient Information Management System (PIMS)

A comprehensive data management system designed to streamline the processing of patient information. Developed using Django, this project operates within an SQLite environment, providing a robust and efficient solution for managing healthcare-related data.

**Note**: This project is an adapted version, and all rights belong to the original developer, Sumit Kumar. It is utilized solely for educational purposes, and all credits go to the original developer.

## Features Added:

- **Date & Scheduling Appointment:** Enables appointment scheduling for Admin, Doctors, and Patients (requires approval).
- **Authentication:** Implemented for Staff, Doctors, and Patients.
- **Updated Admin(Staff):** Allows Admin to update Doctor profiles soon Patients.
- **Doctor Appointment Scheduling:** Doctors can schedule/book appointments for patients within their department.
- **Patient Appointment Booking:** Patients can book appointments too, but require some pending approval from Staff Members.

## Bug Fixes and Improvements:

- **Clickable Cards:** Improved user experience by making cards clickable instead of plain text.
- **Static Icons:** Added static icons to replace deprecated icon links.

## Planning to Add:

- **Admin(Staff) Profile Update:** Enhancement to enable Admin(Staff) to update Doctor and Patients profiles.
- **Patient Overhaul Form:** Addition of a comprehensive form for demographic information and insurance details.

## Requirements and Installation Instructions

### 1. Python Installation:

#### For Windows:

1. Download the latest Python installer for Windows from [python.org](https://www.python.org/downloads/).
2. Run the installer and check "Add Python to PATH" during installation.
3. Verify the installation by opening a Command Prompt and running:

    ```bash
    python --version
    ```

#### For macOS:

1. Check if Python is installed by running:

    ```bash
    python3 --version
    ```

    If not, install using [Homebrew](https://brew.sh/):

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

Ensure Python is added to the system PATH. Open a new terminal/command prompt window and run:

```bash
python --version
```

If it returns the Python version, you're set. If not, update your system PATH.

### 3. SQLite Installation:

SQLite comes bundled with Python; no separate installation is usually needed.

### 4. SQLiteStudio:

Use [SQLiteStudio](https://sqlitestudio.pl/) as a GUI tool for managing SQLite databases. Download and install it according to your operating system.

---

With these tools installed and Python in your system PATH, proceed with setting up the Patient Information Management System as described in the previous README section.

Note: Ensure administrative privileges for installing Python and modifying the system PATH.

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
