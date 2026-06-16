import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import index as indexRoute
from dependencies.config import conf


app = FastAPI()

from fastapi.responses import HTMLResponse

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