import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import index as indexRoute
from dependencies.config import conf
from routers import auth
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
print("AUTH ROUTES:")
for route in auth.router.routes:
    print(route.path)

print("APP ROUTES:")
for route in app.routes:
    print(route.path)
    

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