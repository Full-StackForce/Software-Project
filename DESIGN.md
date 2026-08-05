# PulsePoint Design Document

## PulsePoint
**Team:** Full-StackForce

**Team Members**
- Jennifer Vazquez
- Diya Patel
- Ananya Patchigolla
- Sean Enohmbi
- Niahya Green

---

# 1. Project Overview

PulsePoint is a web-based fitness and wellness application that allows users to manage their health in one centralized platform. The application enables users to create an account, securely log in, and monitor various aspects of their wellness, including workouts, hydration, nutrition, sleep, mood, habits, goals, and weight progress.

The application is built using FastAPI for the backend, MySQL for persistent data storage, SQLAlchemy for database interaction, and HTML/CSS/JavaScript for the frontend.

---

# 2. Objectives

The objectives of PulsePoint are to:

- Provide secure user authentication.
- Store user information in a persistent database.
- Allow users to create, edit, view, and delete wellness data.
- Track personal fitness progress over time.
- Provide a simple and responsive interface.
- Encourage healthy habits through goal tracking.

---

# 3. Functional Requirements

### Authentication
- User Registration
- User Login
- User Logout
- Session Management

### Workout Tracking
- Create workouts
- View workout history
- Update workouts
- Delete workouts

### Habit Tracking
- Create daily habits
- Mark habits as completed
- Edit habits
- Delete habits

### Goal Tracking
- Create goals
- Update goals
- Delete goals

### Weight Tracking
- Log weight entries
- View weight history
- Delete entries

### Dashboard
- Display wellness statistics
- Display completed habits
- Display workout summaries

---

# 4. System Architecture

PulsePoint follows a layered architecture.

Frontend
- HTML
- CSS
- JavaScript

↓

FastAPI Backend

↓

Controllers

↓

SQLAlchemy ORM

↓

MySQL Database

The frontend communicates with the FastAPI API through HTTP requests. The controllers contain the application's business logic, which interacts with SQLAlchemy models to retrieve and store information inside MySQL.

---

# 5. Technologies Used

| Technology | Purpose |
|------------|---------|
| FastAPI | Backend API |
| Python | Programming Language |
| SQLAlchemy | ORM |
| MySQL | Database |
| HTML | Frontend Structure |
| CSS | Styling |
| JavaScript | Client-side Logic |
| Uvicorn | ASGI Server |
| Pydantic | Data Validation |

---

# 6. Database Design

The database stores persistent information for users and wellness tracking.

Primary entities include:

- Users
- Workouts
- Habits
- Goals
- Weight Logs
- Challenges

Relationships

- One User → Many Workouts
- One User → Many Habits
- One User → Many Goals
- One User → Many Weight Logs
- One User → Many Challenge Records

---

# 7. CRUD Operations

The application supports full CRUD functionality.

### Create
- Register user
- Add workout
- Add habit
- Add goal
- Add weight log

### Read
- View dashboard
- View workouts
- View habits
- View goals
- View weight history

### Update
- Edit workouts
- Edit habits
- Edit goals
- Update profile information

### Delete
- Delete workouts
- Delete habits
- Delete goals
- Delete weight entries

---

# 8. Authentication

Authentication is implemented using FastAPI.

Features include:

- User account creation
- Login validation
- Session management
- Protected routes
- User-specific data access

Only authenticated users can access personal fitness information.

---

# 9. Compute Functionality

PulsePoint performs several computations including:

- Daily hydration totals
- Habit completion percentages
- Workout summaries
- Goal progress
- Dashboard statistics
- Challenge completion tracking

These values are calculated dynamically from the stored user data.

---

# 10. Data Persistence

All application data is stored inside a MySQL database.

Persistent data includes:

- User accounts
- Workouts
- Habits
- Goals
- Weight logs
- Challenges

SQLAlchemy provides communication between the application and the database.

---

# 11. Project Structure

```
main.py
controllers/
routers/
models/
schemas/
dependencies/
frontend/
requirements.txt
README.md
DESIGN.md
UML.pdf
```

Directory descriptions:

- **controllers/** – business logic
- **routers/** – API endpoints
- **models/** – SQLAlchemy models
- **schemas/** – request/response validation
- **frontend/** – HTML, CSS, JavaScript
- **dependencies/** – database configuration

---

# 12. API Design

The API is organized into multiple routers.

Examples include:

- Authentication
- Users
- Workouts
- Habits
- Goals
- Dashboard
- Weight Logs
- Challenges

Each router follows RESTful design principles and supports CRUD operations where appropriate.

---

# 13. User Interface

The frontend provides pages for:

- Login
- Registration
- Dashboard
- Workout Tracking
- Habit Tracking
- Goal Tracking
- Weight Tracking
- Challenge Management

The interface communicates with the FastAPI backend using asynchronous HTTP requests.

---

# 14. Future Improvements

Future versions of PulsePoint could include:

- Mobile application
- Push notifications
- Wearable device integration
- Nutrition barcode scanner
- Social features
- Progress charts
- AI workout recommendations
- Calendar synchronization

---

# 15. Conclusion

PulsePoint provides users with a centralized wellness platform that combines authentication, session management, CRUD functionality, database persistence, and real-time wellness tracking. The modular FastAPI architecture allows the application to remain scalable and maintainable while supporting future feature expansion.
