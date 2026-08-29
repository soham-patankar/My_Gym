import json
import os
from datetime import date
import requests 

DATA_FILE = "workouts.json"


def load_workouts():
    if not os.path.exists(DATA_FILE):
       print("No workouts logged yet") 
       return []
    else:
       with open(DATA_FILE,"r") as f: 
            return json.load(f)

def save_workouts(workouts):
    with open(DATA_FILE,"w") as f:
         json.dump(workouts,f,indent=2)

def fetch_exercises(muscle_group):
    API_KEY = "eV1kaA1DnfPeMjuwxqu2LIclcIX1KYvSw9GMs22c" #eV1kaA1DnfPeMjuwxqu2LIclcIX1KYvSw9GMs22c
    url = f"https://api.api-ninjas.com/v1/exercises?muscle={muscle_group}"
    headers = {"X-Api-Key": API_KEY}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if not data:
            print("No exercises found for that muscle group.")
            return None
        
        for i, exercise in enumerate(data):
            print(f"{i+1}. {exercise['name']}")
        
        choice = int(input("Pick a number: "))
        return data[choice - 1]["name"]
    else:
        print(f"API error: {response.status_code}")
        return None
    

def add_workouts(workouts):
    workout_date=str(input("Enter the date of the workout ").strip())
    if not workout_date:
       workout_date=str(date.today())
    muscle_group=input("Enter the muscle you want to train \nChest/Shoulders/Triceps/Lats/Biceps/Forearms/Quadriceps/Hamstrings/Calves: \n").strip()
    exercise=fetch_exercises(muscle_group)
    sets=int(input("Enter the number of sets "))
    reps=int(input("Enter the number of reps "))
    weight=float(input("Enter the total weight (kg) "))
    id=len(workouts)+1
    workout={
           "id":id,
           "workout_date":workout_date,
           "exercise":exercise,
           "sets":sets,
           "reps":reps,
           "weight":weight
    }
    workouts.append(workout)
    save_workouts(workouts)
    print("Workout added successfully")

def view_workouts(workouts):
    if len(workouts)<1:
       print("No workouts has been logged yet")
    else:
       for w in workouts:
           print(f'{w["id"]} {w["exercise"]} {w["sets"]} sets for {w["reps"]} reps @ {w["weight"]}kg on {w["workout_date"]}')

def delete_workouts(workouts):
    view_workouts(workouts)
    wid=int(input("Enter the Id to delete the specific workout "))
    workouts[:] = [w for w in workouts if w["id"] != wid]
    save_workouts(workouts)
    print("The workout has been deleted successfully")



def main_menu():
    workouts=load_workouts()
    while True:
        print("--Select the option--")
        print("1. Add workout")
        print("2.View workout")
        print("3.Delete workout")
        print("4.Exit")
        choice=int(input("Enter the option: "))    
        if  choice==1:
            add_workouts(workouts)
        elif choice==2:
            view_workouts(workouts)
        elif choice==3:
            delete_workouts(workouts)
        elif choice==4:
            break
        else:
            print("Wrong Input")               

if __name__=="__main__":
   main_menu()
    