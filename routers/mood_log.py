from datetime import datetime
import json
import os

DATA_FILE = "moods.json"


def load_moods():
    """Loads existing mood entries from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_moods(moods):
    """Saves updated mood entries back to the JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(moods, file, indent=4)


def log_mood():
    """Prompts user for mood details and records entry."""
    print("\n--- Log Your Mood ---")
    print("Options: 1. Great | 2. Good | 3. Neutral | 4. Down | 5. Stressed")

    mood_map = {
        "1": "Great",
        "2": "Good",
        "3": "Neutral",
        "4": "Down",
        "5": "Stressed",
    }
    choice = input("Select mood (1-5) or enter a custom word: ").strip()
    mood = mood_map.get(choice, choice.capitalize() if choice else "Neutral")

    note = input("Add a brief note/journal entry (optional): ").strip()

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mood": mood,
        "note": note,
    }

    moods = load_moods()
    moods.append(entry)
    save_moods(moods)

    print(f"\nSaved! Added: [{entry['timestamp']}] {mood}")


def view_history():
    """Displays stored mood history."""
    moods = load_moods()
    if not moods:
        print("\nNo mood entries found yet.")
        return

    print("\n--- Mood History ---")
    for item in moods[-10:]:  # Shows last 10 entries
        note_str = f" | Note: {item['note']}" if item.get("note") else ""
        print(f"[{item['timestamp']}] {item['mood']}{note_str}")


def view_summary():
    """Shows frequency count of each logged mood."""
    moods = load_moods()
    if not moods:
        print("\nNo mood data to summarize.")
        return

    summary = {}
    for entry in moods:
        m = entry["mood"]
        summary[m] = summary.get(m, 0) + 1

    print("\n--- Mood Summary ---")
    for mood, count in summary.items():
        print(f"• {mood}: {count} time(s)")


def main():
    while True:
        print("\n=====================")
        print("    MOOD TRACKER     ")
        print("=====================")
        print("1. Log today's mood")
        print("2. View recent history")
        print("3. View summary")
        print("4. Exit")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            log_mood()
        elif choice == "2":
            view_history()
        elif choice == "3":
            view_summary()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
