import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import index as indexRoute
from fastapi.responses import HTMLResponse

from routers import index as indexRoute
from routers import goal as goalRoute
from routers import auth
from dependencies.config import conf
from routers import workout as workoutRoute
from routers import habit as habitRoute


app = FastAPI()

from fastapi.responses import HTMLResponse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goalRoute.router)
app.include_router(workoutRoute.router)
app.include_router(habitRoute.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>PulsePoint</title>
        </head>
        <body>
            <h1>PulsePoint</h1>
            <p>Welcome to PulsePoint!</p>

            <h2>Features</h2>
            <ul>
                <li>Habit Tracking</li>
                <li>Workout Tracking</li>
                <li>Goals</li>
                <li>Dashboard</li>
            </ul>

            <button onclick="document.getElementById('workoutForm').style.display='block'">
            Enter Workout
            </button>

            <form id ="workoutForm" style="display:none; margin-top:20px;">
                <h2>Log Workout</h2>

                <label for="user_id">User ID:</label><br>
                <input type="number" id="user_id" value="1"required> <br><br>

                <label for="type">Workout Type:</label><br>
                <input type="text" id="type" placeholder = "workout type" required> <br><br>

                <label for="duration_minutes">Workout Duration:</label><br>
                <input type="number" id="duration_minutes" placeholder="Duration in minutes" required> <br><br>

                <label for="calories_burned">Calories burned:</label><br>
                <input type="number" id="calories_burned" placeholder="Calories burned"required> <br><br>

                <label for="mood_level">Mood Level:</label><br>
                <select id="mood_level" required>
                    <option value="1">1 - Not good</option>
                    <option value="2">2</option>
                    <option value="3">3 - Average</option>
                    <option value="4">4</option>
                    <option value="5">5 Went really well</option>
                </select><br><br>

                <label for="notes">Notes:</label><br>
                <textarea id="notes" placeholder="Did anything affect your workout?"></textarea><br><br>

                <button type="submit">Save Workout</button>
                </form>

                <h2>Workout History</h2>
                <div id ="workoutList"></div>
                <button onclick="document.getElementById('habitSection').style.display='block'">
            Habit Tracking
        </button>

        <div id="habitSection" style="display:none; margin-top:20px;">
            <h2>Create Habit</h2>

            <form id="habitForm">

                <label for="habit_user_id">User ID:</label><br>
                <input type="number" id="habit_user_id" value="1" required><br><br>

                <label for="habit_name">Habit Name:</label><br>
                <input type="text" id="habit_name" placeholder="Habit name" required><br><br>

                <label for="habit_description">Description:</label><br>
                <input type="text" id="habit_description" placeholder="Optional description"><br><br>

                <label for="habit_frequency">Frequency:</label><br>
                <input type="text" id="habit_frequency" placeholder="Frequency, ex: daily" required><br><br>

                <label for="habit_target_count">Target Count:</label><br>
                <input type="number" id="habit_target_count" placeholder="Target count" required><br><br>

                <button type="submit">Save Habit</button>
            </form>

            <h2>Active Habits</h2>
            <div id="habitList"></div>

            <h2>Habit History</h2>
            <div id="habitHistory"></div>
        </div>

                <script>
                    document.getElementById("workoutForm").addEventListener("submit", async function(e) {
                    e.preventDefault();

                    const workout = {
                        user_id: Number(document.getElementById("user_id").value),
                        type: document.getElementById("type").value,
                        duration_minutes: Number(document.getElementById("duration_minutes").value),
                        calories_burned: Number(document.getElementById("calories_burned").value),
                        mood_level: Number(document.getElementById("mood_level").value),
                        notes: document.getElementById("notes").value
                    };

                    const response = await fetch("/workouts/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(workout)
                    });

                    if (response.ok) {
                        alert("Workout saved!");
                        document.getElementById("workoutForm").reset();
                        loadWorkouts();
                    } else {
                        alert("Workout could not be saved.");
                    }
                });

                async function loadWorkouts() {
                    const response = await fetch("/workouts/");
                    const workouts = await response.json();

                    const list = document.getElementById("workoutList");
                    list.innerHTML = "";

                    workouts.forEach(workout => {
                        list.innerHTML += `
                            <div style="border:1px solid #ccc; padding:10px; margin:10px 0;">
                                <strong>${workout.type}</strong><br>
                                Duration: ${workout.duration_minutes} minutes<br>
                                Calories: ${workout.calories_burned}<br>
                                Mood: ${workout.mood_level}/5<br>
                                Notes: ${workout.notes || "No notes"}<br>
                                Completed: ${workout.completed_at}
                            </div>
                        `;
                    });
                }

                loadWorkouts();

                document.getElementById("habitForm").addEventListener("submit", async function(e) {
                    e.preventDefault();

                    const habit = {
                        user_id: Number(document.getElementById("habit_user_id").value),
                        name: document.getElementById("habit_name").value,
                        description: document.getElementById("habit_description").value,
                        frequency: document.getElementById("habit_frequency").value,
                        target_count: Number(document.getElementById("habit_target_count").value)
                    };

                    const response = await fetch("/habits/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(habit)
                    });

                    if (response.ok) {
                        alert("Habit saved!");
                        document.getElementById("habitForm").reset();
                        document.getElementById("habit_user_id").value = 1;
                        loadHabits();
                    } else {
                        alert("Habit could not be saved.");
                    }
                });

                async function loadHabits() {
                    const userId = document.getElementById("habit_user_id").value || 1;
                    const response = await fetch(`/habits/${userId}`);
                    const habits = await response.json();

                    const list = document.getElementById("habitList");
                    list.innerHTML = "";

                    habits.forEach(habit => {
                        list.innerHTML += `
                            <div style="border:1px solid #ccc; padding:10px; margin:10px 0;">
                                <strong>${habit.name}</strong><br>
                                Description: ${habit.description || "No description"}<br>
                                Frequency: ${habit.frequency}<br>
                                Target Count: ${habit.target_count}<br>
                                Streak: ${habit.streak_count}<br>
                                Completed Today: ${habit.completed_today}<br>
                                Last Completed: ${habit.last_completed_date || "Not completed yet"}<br><br>

                                <button onclick="completeHabit(${habit.id})">Mark Complete</button>
                                <button onclick="deleteHabit(${habit.id})">Delete</button>
                            </div>
                        `;
                    });
                }

                async function completeHabit(habitId) {
                    const response = await fetch(`/habits/${habitId}/complete`, {
                        method: "POST"
                    });

                    if (response.ok) {
                        alert("Habit marked complete!");
                        loadHabits();
                        loadHabitHistory();
                    } else {
                        alert("Could not mark habit complete.");
                    }
                }

                async function deleteHabit(habitId) {
                    const response = await fetch(`/habits/${habitId}`, {
                        method: "DELETE"
                    });

                    if (response.ok) {
                        alert("Habit deleted!");
                        loadHabits();
                    } else {
                        alert("Could not delete habit.");
                    }
                }

                async function loadHabitHistory() {
                    const userId = document.getElementById("habit_user_id").value || 1;
                    const response = await fetch(`/habits/history/${userId}`);
                    const history = await response.json();

                    const historyDiv = document.getElementById("habitHistory");
                    historyDiv.innerHTML = "";

                    history.forEach(item => {
                        historyDiv.innerHTML += `
                            <div style="border:1px solid #ddd; padding:8px; margin:8px 0;">
                                Habit ID: ${item.habit_id}<br>
                                Completed Date: ${item.completed_date}
                            </div>
                        `;
                    });
                }

                loadHabits();
                loadHabitHistory();

            </script>
        </body>
    </html>
    """


@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
    <html>
    <head>
        <title>Login</title>
    </head>
    <body>
        <h2>Login</h2>

        <form id="loginForm">
            <input type="email" id="email" placeholder="Email" required />
            <br><br>
            <input type="password" id="password" placeholder="Password" required />
            <br><br>
            <button type="submit">Login</button>
        </form>

        <p id="message"></p>

        <script>
            document.getElementById("loginForm").addEventListener("submit", async function(e) {
                e.preventDefault();

                const email = document.getElementById("email").value;
                const password = document.getElementById("password").value;

                const response = await fetch("/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    document.getElementById("message").innerText = "Login successful!";
                    window.location.href = "/dashboard";
                } else {
                    document.getElementById("message").innerText = data.detail;
                }
            });
        </script>
    </body>
    </html>
    """


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
    <head>
        <title>PulsePoint Dashboard</title>
    </head>
    <body>
        <h1>PulsePoint Dashboard</h1>

        <h2>Welcome Back!</h2>

        <ul>
            <li>View Habits</li>
            <li>Track Workouts</li>
            <li>Manage Goals</li>
            <li>View Progress</li>
        </ul>

        <a href="/login">Logout</a>
    </body>
    </html>
    """