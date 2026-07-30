# PulsePoint

## Project Description

PulsePoint is a fitness and wellness application that helps users track workouts, sleep, water intake, nutrition, mood, and daily habits. The goal is to help users stay consistent with their health and fitness goals by keeping all important wellness information in one place.

## Setup

1. Create and activate a virtual environment.
2. Install the project dependencies:

```bash
pip install -r requirements.txt
```
4. Connect to mysql database in dependancies file

5. Start the application with Uvicorn:

```bash
uvicorn main:app --reload
```

6. Open `https://pulsepointtrain.com/` to use the site, or `https://pulsepointtrain.com/docs` to view the API and CRUD routes.

## Project Structure

- `main.py` starts the FastAPI app and registers the routers.
- `controllers/` contains the business logic for users, workouts, habits, goals, dashboard data, and weight logs.
- `routers/` exposes the HTTP endpoints for each feature area.
- `models/` contains SQLAlchemy models.
- `schemas/` contains Pydantic request and response models.
- `dependencies/` contains database and configuration setup.
- `frontend/` contains the static HTML pages served by the app.

## Project Team

- Jennifer Vazquez
- Diya Patel
- Ananya Patchigolla
- Sean Enohmbi
- Mohamed Shire
- Niahya Green

## Scrum Team

### Product Owner
Sean Enohmbi

### Scrum Master
Jennifer Vazquez

### Developers
Ananya Patchigolla
Niahya Green
Diya Patel
Mohamed Shire

## Sprint 1 Goal

Set up the project repository, Scrum board, and user stories for Sprint Demo 1.


