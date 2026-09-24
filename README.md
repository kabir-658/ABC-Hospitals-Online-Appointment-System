# ABC Group of Hospitals Online Appointment System

A Flask-based implementation for the Week 9 Software Development Lifecycle activity. The project uses an Agile implementation approach, SQLite database storage, password hashing, validation, role-based access, appointment booking, simulated online payment, support requests, an admin dashboard, appointment history and pytest tests.

## Core modules
1. Patient Registration
2. Patient Login
3. Doctor Management
4. Appointment Booking
5. Online Payment (simulated for academic use)
6. Customer Support
7. Admin Dashboard
8. Appointment History

## Run in PyCharm
1. Open the `PythonProject1` folder in PyCharm.
2. Create/select a Python virtual environment.
3. Install packages from `requirements.txt`.
4. Run `app.py`.
5. Open the Flask URL shown in the PyCharm terminal.

## Demo admin account
- Email: `admin@abc-hospitals.com`
- Password: `Admin@123`

Change the demo password before any real deployment. This project is for academic demonstration and the payment process is intentionally simulated.

## Testing
Run:

```bash
pytest -q
```

The tests cover registration/login, invalid login, role protection, appointment booking, duplicate slot rejection, payment confirmation, support submission and doctor management.

## Git and progress documentation
The project is structured for Git version control. `DEVELOPMENT_LOG.md` records implementation stages and the `.git` folder contains local commit history. Push the repository to GitHub from PyCharm for the required GitHub evidence.
