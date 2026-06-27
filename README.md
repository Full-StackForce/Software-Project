# PulsePoint

## Project Description

PulsePoint is a fitness and wellness application that helps users track workouts, sleep, water intake, nutrition, mood, and daily habits. The goal is to help users stay consistent with their health and fitness goals by keeping all important wellness information in one place.

##  Setup

1. Create and activate a virtual environment.
2. Install the project dependencies:

```bash
pip install -r requirements.txt
```

3. Configure the MySQL database by updating the settings in dependencies/config.py, then make sure your MySQL server is running before starting the application.
4. Start the application:
```bash
uvicorn main:app --reload
```

5. Open the application:

- http://127.0.0.1:8000/

6. Open the FastAPI Swagger documentation:

- http://127.0.0.1:8000/docs

 ## Testing the Application

1. Start the application:

```bash
uvicorn main:app --reload
```

2. Open:

http://127.0.0.1:8000/

3. Open Swagger:

http://127.0.0.1:8000/docs

4. Test the available API endpoints:

* Authentication
* Users
* Workouts
* Goals
* Habits
* Dashboard

5. Verify that GET and POST requests return successful responses and that the application starts without errors.

##  Project Structure

* main.py starts the FastAPI application and registers the routers.
* controllers/ contains the business logic.
* routers/ exposes the API endpoints.
* models/ contains the SQLAlchemy models.
* schemas/ contains the Pydantic schemas.
* dependencies/ contains database configuration.
* frontend/ contains the frontend pages.

##  Project Team

* Jennifer Vazquez
* Diya Patel
* Ananya Patchigolla
* Sean Enohmbi
* Mohamed Shire
* Niahya Green

##  Scrum Team

### Product Owner
-Sean Enohmbi

### Scrum Master
-Jennifer Vazquez

### Developers
- Ananya Patchigolla
- Niahya Green
- Diya Patel
- Mohamed Shire

## Team Contributions

Jennifer Vazquez

* Scrum Master
* Sprint planning and Scrum coordination.

Sean Enohmbi

* Product Owner
* Product planning, backlog management, and sprint coordination.

Diya Patel

* Authentication (login) implementation and frontend/backend integration.

Ananya Patchigolla

* Frontend development and user interface implementation.

Niahya Green

* Project structure, backend/frontend updates, dependency configuration, and design documentation.

Mohamed Shire

* Scrum board management and sprint organization.
* Goal feature development and Goal schema updates.
* FastAPI API testing and workout endpoint validation.
* Project debugging, verification, and GitHub integration.

## Sprint 1 Goal

Set up the project repository, Scrum board, and user stories for Sprint Demo 1.

 ##  Sprint 2 Goal

Develop a working PulsePoint prototype that demonstrates user authentication, CRUD functionality, FastAPI backend integration, database connectivity, and frontend pages. Verify that the application runs successfully and that the implemented features can be tested through the web interface and the FastAPI Swagger documentation.
