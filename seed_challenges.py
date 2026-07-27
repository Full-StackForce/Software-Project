from dependencies.database import SessionLocal, engine, Base
from models.challenge import Challenge
from models.challenge_completion import ChallengeCompletion  # noqa: F401 (ensures table registers)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

seed_data = [
    {
        "title": "Drink 2.5L Water",
        "description": "Stay hydrated throughout the day.",
        "category": "hydration",
        "icon": "💧",
        "xp_reward": 10,
        "target_value": 2.5,
        "unit": "liters",
        "challenge_type": "daily",
    },
    {
        "title": "Sleep 8 Hours",
        "description": "Get a full night's sleep.",
        "category": "sleep",
        "icon": "💤",
        "xp_reward": 15,
        "target_value": 8,
        "unit": "hours",
        "challenge_type": "daily",
    },
    {
        "title": "Complete a Workout",
        "description": "Finish any workout today.",
        "category": "workout",
        "icon": "🏋️",
        "xp_reward": 20,
        "target_value": 1,
        "unit": "workout",
        "challenge_type": "daily",
    },
    {
        "title": "10,000 Steps",
        "description": "Reach today's step goal.",
        "category": "steps",
        "icon": "🚶",
        "xp_reward": 15,
        "target_value": 10000,
        "unit": "steps",
        "challenge_type": "daily",
    },
]

try:
    for entry in seed_data:
        existing = db.query(Challenge).filter(Challenge.title == entry["title"]).first()
        if existing:
            print(f"Skipping (already exists): {entry['title']}")
            continue
        db.add(Challenge(**entry))
        print(f"Added: {entry['title']}")

    db.commit()
    print("Seeding complete.")
finally:
    db.close()

    {
        "title": "Walk 50,000 Steps",
        "description": "Walk 50,000 steps before Sunday.",
        "category": "steps",
        "icon": "🚶",
        "xp_reward": 50,
        "target_value": 50000,
        "unit": "steps",
        "challenge_type": "weekly",
    },
