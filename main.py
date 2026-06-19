import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from routers import index as indexRoute
from routers import goal as goalRoute
from routers import auth
from dependencies.config import conf
from routers import workout as workoutRoute


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goalRoute.router)
app.include_router(workoutRoute.router)
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

                <input type="number" id="user_id" value="1"required> <br><br>
                <input type="text" id="type" placeholder = "workout type" required> <br><br>
                <input type="number" id="duration_minutes" placeholder="Duration in minutes" required> <br><br>
                <input type="number" id="calories_burned" placeholder="Calories burned"required> <br><br>

                <select id="mood_level" required>
                    <option value="1">1 - Not good</option>
                    <option value="2">2</option>
                    <option value="3">3 - Average</option>
                    <option value="4">4</option>
                    <option value="5">5 Went really well</option>
                </select><br><br>

                <textarea id="notes" placeholder="Did anything affect your workout?"></textarea><br><br>

                <button type="submit">Save Workout</button>
                </form>

                <h2>Workout History</h2>
                <div id ="workoutList"></div>

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
    <h1>Dashboard</h1>
    <p>Welcome! You are logged in.</p>
    """