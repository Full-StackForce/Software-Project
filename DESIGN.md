## PulsePoint Design

### Overview

PulsePoint is a full-stack wellness tracker built with FastAPI on the backend and static HTML pages on the frontend. The application focuses on a clear dashboard experience for tracking workouts, habits, goals, weight, sleep, and other wellness data.

### Architecture

The backend follows a simple layered structure:

- `main.py` creates the FastAPI application, mounts static files, and registers routers.
- `routers/` exposes HTTP routes for each feature area.
- `controllers/` contains the business logic for database operations and derived calculations.
- `models/` defines the SQLAlchemy tables.
- `schemas/` defines the Pydantic request and response contracts.
- `dependencies/` handles shared infrastructure such as configuration and database sessions.

### Frontend

The frontend is served as static files from the `frontend/` directory. Pages are organized by feature, including the home dashboard, login, signup, and account views. Shared styling and behavior are kept in reusable CSS and JavaScript files so the pages stay consistent and easier to maintain.

### Data Flow

1. A frontend page sends a request to a FastAPI route.
2. The route calls a controller function.
3. The controller reads or writes data using SQLAlchemy models and a database session.
4. The controller returns model data that is validated or serialized through a Pydantic schema.
5. The frontend updates the UI with the response.

### Key Models

- `User` stores account and profile data.
- `Workout` stores workout logs and session details.
- `Habit` stores daily habit definitions and progress.
- `Goal` stores progress goals tied to habit completion.
- `WeightLog` stores body weight history.
- `LoginActivity` stores login tracking data.

### Styling Approach

The frontend uses semantic helper classes for repeated UI patterns such as panels, fields, buttons, and notifications. This keeps the HTML easier to read while preserving a consistent visual language across pages.

### Dependencies

The runtime dependencies are intentionally small:

- FastAPI for the web framework.
- Uvicorn for the ASGI server.
- SQLAlchemy for database access and ORM models.
- PyMySQL for the MySQL connection driver.
- Pydantic for request and response validation.
- email-validator for validating `EmailStr` fields.
