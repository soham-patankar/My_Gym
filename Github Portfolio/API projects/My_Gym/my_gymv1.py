import json
import os
from datetime import date

DATA_FILE = "workouts.json"


# ---------- file helpers ----------

def load_workouts():
    """Read workouts from the JSON file. Returns an empty list if file doesn't exist yet."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_workouts(workouts):
    """Write the full workouts list back to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(workouts, f, indent=2)


# ---------- core actions ----------

def add_workout(workouts):
    print("\n--- Add Workout ---")

    # Let the user press Enter to default to today's date
    workout_date = input("Date (YYYY-MM-DD) or Enter for today: ").strip()
    if not workout_date:
        workout_date = str(date.today())

    exercise = input("Exercise name: ").strip()
    sets     = int(input("Sets: "))
    reps     = int(input("Reps per set: "))
    weight   = float(input("Weight (kg): "))

    # Build a dict for this workout entry
    workout = {
        "id":       len(workouts) + 1,
        "date":     workout_date,
        "exercise": exercise,
        "sets":     sets,
        "reps":     reps,
        "weight":   weight,
    }

    workouts.append(workout)
    save_workouts(workouts)
    print(f"\n✓ Logged: {exercise} — {sets}x{reps} @ {weight}kg on {workout_date}")


def view_workouts(workouts):
    if not workouts:
        print("\nNo workouts logged yet.")
        return

    print("\n--- Your Workouts ---")
    for w in workouts:
        print(f"[{w['id']}]  {w['date']}  |  {w['exercise']}  |  {w['sets']}x{w['reps']} @ {w['weight']}kg")


def delete_workout(workouts):
    view_workouts(workouts)
    if not workouts:
        return

    try:
        wid = int(input("\nEnter ID to delete: "))
        # Keep every workout whose id does NOT match
        original_len = len(workouts)
        workouts[:] = [w for w in workouts if w["id"] != wid]

        if len(workouts) < original_len:
            save_workouts(workouts)
            print(f"✓ Workout #{wid} deleted.")
        else:
            print("No workout found with that ID.")

    except ValueError:
        print("Please enter a valid number.")


# ---------- main loop ----------

def main():
    workouts = load_workouts()   # load once at startup
    print("=== Workout Logger ===")

    while True:
        print("\n1. Add workout")
        print("2. View workouts")
        print("3. Delete workout")
        print("4. Quit")
        choice = input("\nChoose (1-4): ").strip()

        if choice == "1":
            add_workout(workouts)
        elif choice == "2":
            view_workouts(workouts)
        elif choice == "3":
            delete_workout(workouts)
        elif choice == "4":
            print("See you next session!")
            break
        else:
            print("Invalid choice — enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()