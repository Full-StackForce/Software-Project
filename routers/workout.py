from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from typing import List

from controllers.workout_controller import create_workout, list_workouts
from schemas.workout import WorkoutCreate, WorkoutResponse

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/", response_model=WorkoutResponse)
def create_workout_route(payload: WorkoutCreate):
    return create_workout(payload)


@router.get("/", response_model=List[WorkoutResponse])
def get_workouts():
    return list_workouts()

@router.get("/new", response_class=HTMLResponse)
def new_workout_form():
    return """
      <html>
      <head>   
            <title>Log a Workout</title>
      </head>
      <body>
           <h1>Log a Workout</h1>
           <form action="/workouts/new" method="post">
               <label for="user_id">User ID</label><br>
               <input type="number" id="user_id" name="user_id" required><br><br>

               <label for="workout_id">Workout ID</label><br>
               <input type="text" id="type" name="type" placeholder="e.g. Cardio, Strength,Yoga" required><br><br>
    
               <label for="duration_minutes">Duration (minutes)</label><br>
               <input type="number" id="duration_minutes" name="duration_minutes" required><br><br>
    
               <label for="notes">Notes (optional)</label><br>
               <textarea id="notes" name="notes" rows="3"></textarea><br><br>

               <button type="submit">Submit Workout</button>
            </form>
        </body>
    </html>
    """

@router.post("/new", response_class=HTMLResponse)
def submit_workout_form(
    user_id: int = Form(...),
    type: str = Form(...),
    duration_minutes: int = Form(...),
    notes: str = Form(""),
):
    payload = WorkoutCreate(
        user_id=user_id,
        type=type,
        duration_minutes=duration_minutes,
        calories_burned=None,
        notes=notes or None,
    )
    workout = create_workout(payload)

    return f"""
       <html>
           <head>
               <title>Workout Logged</title>
           </head>
           <body>
               <h1>Workout Logged!</h1>
               <p>Your workout was saved successfully.</p>
               <ul>
                   <li><strong>User ID:</strong> {workout.user_id}</li>
                   <li><strong>Type:</strong> {workout.type}</li>
                   <li><strong>Duration:</strong> {workout.duration_minutes} minutes</li>
                   <li><strong>Notes:</strong> {workout.notes or "-"}</li>
                   <li><strong>Logged at:</strong> {workout.completed_at}</li>
               </ul>
               <p><a href="/workouts/new">Log another workout</a></p>
           </body>
       </html>
       """
