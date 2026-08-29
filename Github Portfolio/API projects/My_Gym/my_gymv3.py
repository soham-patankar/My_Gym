import sqlite3
from datetime import date,datetime
import requests
import dotenv
import os

DATABASE= "workouts.db"

dotenv.load_dotenv()

def init_db():
    connection= sqlite3.connect(DATABASE)
    cursor=connection.cursor()
    
    #WORKOUTS TABLE
    cursor.execute("""CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_name TEXT,
    workout_date TEXT
    )""")

    #EXERCISES TABLE
    cursor.execute("""CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER,
    exercise TEXT,
    sets INTEGER,
    reps INTEGER,
    weight REAL,
    FOREIGN KEY (workout_id) REFERENCES workouts(id)
    )""")


    connection.commit()
    connection.close()

def main_menu():
   init_db()
   while True:
    print("===MAIN MENU===")
    print("1.)---View Workout---")
    print("2.)---Add Workout---")
    print("3.)---Delete Workout---")
    print("4.)---HERE TO EXIT---")
    try: 
     choice=int(input("Enter the option: "))
     if choice==1:
        view_workouts()
     elif choice==2:
        add_workouts()
     elif choice==3:
        delete_workouts()
     elif choice==4:
        exit()   
    except ValueError:
       print("Enter an integer: ")    

def get_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            print("Please enter a number greater than 0")
        except ValueError:
            print("Please enter a valid integer")

def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter an Integer: ")     

def fetch_exercises(muscle_group):
    API_KEY = os.getenv("API_KEY")
    url = f"https://api.api-ninjas.com/v1/exercises?muscle={muscle_group}"
    headers = {"X-Api-Key": API_KEY}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if not data:
            return None
        for i, exercise in enumerate(data):
            print(f"{i+1}. {exercise['name']}")
        while True:
          try:    
             choice=int(input("Enter a number"))
             if 1<=choice<=len(data):
                return data[choice-1]["name"]
             print(f"Please enter a number between 1 and {len(data)}")
          except TypeError:
           print("Not an Integer") 
    else:
        print(f"API error: {response.status_code}")
        return None              

def add_workouts():
    connection= sqlite3.connect(DATABASE)
    cursor=connection.cursor()
    while True:
      workout_name=str(input("Enter the name of workout: "))
      if not workout_name.strip():
        print("No input received please enter name to save")
        continue
      else:
       break 
    while True:
     workout_date = input("Enter the workout date (DD-MM-YYYY) or press Enter for today: ").strip()
    
     if not workout_date:               # Case 1 — empty → use today
        workout_date = str(date.today())
        break
    
     try:                               # Case 2 — something typed → validate
        datetime.strptime(workout_date, r"%d-%m-%Y")
        break                          # valid format → exit loop
     except ValueError:
        print("Invalid format — please use DD-MM-YYYY")  # invalid → loop again 
    cursor.execute("""INSERT INTO workouts(workout_name,workout_date) VALUES(?,?)""",(workout_name,workout_date))  
    workout_id=cursor.lastrowid
    while True:   
      muscle_group=str(input("Enter the muscle group: ")).strip()
      exercise=fetch_exercises(muscle_group)
      if exercise is None:
        print("Please Enter Valid Muscle Group: ")
        continue
      sets=get_positive_int("Enter the number of sets: ")
      reps=get_positive_int("Enter the number of reps: ")
      weight=get_positive_int("Enter the total weight lifted in kg: ")   
      cursor.execute("""INSERT INTO exercises(workout_id,exercise,sets,reps,weight) VALUES(?,?,?,?,?)""",(workout_id,exercise,sets,reps,weight))
      again=str(input("Do you want to add another exercise in the workout ? \nPress any button to continue or Press N to Quit "))
      if again.upper()=="N":
        break
    connection.commit()
    connection.close()


def view_workouts():
    connection=sqlite3.connect(DATABASE)
    cursor=connection.cursor()
    cursor.execute("""SELECT * from workouts""")
    results=cursor.fetchall()
    for row in results:
        print(f"[{row[0]}] {row[1]}")
    connection.close()    
    if results:
       wid=int(input("Enter the workout ID to be viewed"))
       if wid!=0:
          view_exercises(wid)

def view_exercises(workout_id):
    connection=sqlite3.connect(DATABASE)
    cursor=connection.cursor()
    cursor.execute("SELECT * from exercises WHERE workout_id=?",(workout_id,))
    reveal=cursor.fetchall()
    for row in reveal:
       print(f"[{row[0]}][{row[1]}]{row[2]} of {row[3]} sets for {row[4]} reps at {row[5]}kg")
    connection.close()   

def delete_workouts():
    connection = sqlite3.connect(DATABASE)    
    cursor = connection.cursor()
    while True:
        wid = get_int("Enter the ID to be deleted: ")
        cursor.execute("SELECT id FROM workouts WHERE id=?", (wid,))
        result = cursor.fetchone()
        if result is None:
            print("Please enter a valid ID: ")
        else:
            cursor.execute("DELETE FROM exercises WHERE workout_id=?", (wid,))  # ← delete exercises first
            cursor.execute("DELETE FROM workouts WHERE id=?", (wid,))           # ← then delete workout
            connection.commit()
            print(f"Workout {wid} and all its exercises deleted.")
            break     
    connection.close()

if __name__=="__main__":main_menu()