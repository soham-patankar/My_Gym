import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

from gymlocker_api import get_exercises


# ============================================================
# DATABASE
# ============================================================

DB_FILE = "gym_locker.db"


def get_connection():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # --------------------------------------------------------
    # Workouts
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # Exercises belonging to a workout
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            exercise_name TEXT NOT NULL,
            muscle TEXT NOT NULL,

            FOREIGN KEY (workout_id)
                REFERENCES workouts(id)
                ON DELETE CASCADE
        )
    """)

    # --------------------------------------------------------
    # Sets belonging to an exercise
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_id INTEGER NOT NULL,
            set_number INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL NOT NULL,

            FOREIGN KEY (exercise_id)
                REFERENCES workout_exercises(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def save_workout(workout_name, workout_exercises):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON")

        # ----------------------------------------------------
        # Create workout
        # ----------------------------------------------------
        cursor.execute("""
            INSERT INTO workouts (name, created_at)
            VALUES (?, ?)
        """, (
            workout_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        workout_id = cursor.lastrowid

        # ----------------------------------------------------
        # Create exercises
        # ----------------------------------------------------
        for exercise_data in workout_exercises:

            cursor.execute("""
                INSERT INTO workout_exercises
                (workout_id, exercise_name, muscle)
                VALUES (?, ?, ?)
            """, (
                workout_id,
                exercise_data["exercise"],
                exercise_data["muscle"]
            ))

            exercise_id = cursor.lastrowid

            # ------------------------------------------------
            # Create sets
            # ------------------------------------------------
            for set_data in exercise_data["sets"]:

                cursor.execute("""
                    INSERT INTO exercise_sets
                    (exercise_id, set_number, reps, weight)
                    VALUES (?, ?, ?, ?)
                """, (
                    exercise_id,
                    set_data["set_number"],
                    set_data["reps"],
                    set_data["weight"]
                ))

        conn.commit()

        return workout_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_workouts():
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            id,
            name,
            created_at
        FROM workouts
        ORDER BY created_at DESC
    """, conn)

    conn.close()

    return df


def get_workout_details(workout_id):
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            w.id AS workout_id,
            w.name AS workout,
            w.created_at,
            e.id AS exercise_id,
            e.exercise_name AS exercise,
            e.muscle,
            s.set_number,
            s.reps,
            s.weight

        FROM workouts w

        JOIN workout_exercises e
            ON w.id = e.workout_id

        JOIN exercise_sets s
            ON e.id = s.exercise_id

        WHERE w.id = ?

        ORDER BY
            e.id,
            s.set_number
    """, conn, params=(workout_id,))

    conn.close()

    return df


# ============================================================
# INITIALISE DATABASE
# ============================================================

init_db()


# ============================================================
# MUSCLES
# ============================================================

MUSCLES = {
    "Chest": "chest",
    "Traps": "traps",
    "Triceps": "triceps",
    "Biceps": "biceps",
    "Lats": "lats",
    "Middle Back": "middle_back",
    "Lower Back": "lower_back",
    "Quadriceps": "quadriceps",
    "Hamstrings": "hamstrings",
    "Glutes": "glutes",
    "Calves": "calves",
    "Abdominals": "abdominals",
}


# ============================================================
# SESSION STATE
# ============================================================

if "workout_exercises" not in st.session_state:
    st.session_state["workout_exercises"] = []

if "searched" not in st.session_state:
    st.session_state["searched"] = False

if "exercises" not in st.session_state:
    st.session_state["exercises"] = []


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Gym LOCKer",
    page_icon="🏋️",
    layout="wide"
)


st.markdown(
    "<h1 style='color:#FFFFFF;'>Gym LOCKer</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<h3 style='color:#FFFFFF;'>Measure your strength. To surpass your limits</h3>",
    unsafe_allow_html=True
)


# ============================================================
# TABS
# ============================================================

create_tab, history_tab = st.tabs([
    "🏋️ Create Workout",
    "📚 Workout History"
])


# ============================================================
# CREATE WORKOUT
# ============================================================

with create_tab:

    st.header("Create Workout")

    workout_name = st.text_input(
        "Workout Name:",
        placeholder="Type here...."
    )

    muscle_label = st.selectbox(
        "Select a muscle:",
        list(MUSCLES.keys())
    )

    # --------------------------------------------------------
    # Search exercises
    # --------------------------------------------------------

    if st.button("Search Exercises"):

        try:

            with st.spinner("Searching exercises..."):

                api_response = get_exercises(
                    MUSCLES[muscle_label]
                )

            st.session_state["exercises"] = [
                item["name"]
                for item in api_response
            ]

            st.session_state["searched"] = True

        except Exception as e:

            st.session_state["searched"] = False

            st.error(
                f"Could not retrieve exercises: {e}"
            )

    # --------------------------------------------------------
    # Exercise selection
    # --------------------------------------------------------

    if st.session_state.get("searched", False):

        exercises = st.session_state.get(
            "exercises",
            []
        )

        if not exercises:

            st.warning(
                "No exercises found for this muscle."
            )

        else:

            exercise = st.selectbox(
                "Select an exercise:",
                exercises
            )

            setr = st.number_input(
                "Number of Sets",
                min_value=1,
                max_value=12,
                value=3,
                step=1
            )

            data = pd.DataFrame({
                "Set": range(1, int(setr) + 1),
                "Reps": [10] * int(setr),
                "Weight (kg)": [0.0] * int(setr)
            })

            st.subheader(exercise)

            edited_data = st.data_editor(
                data,
                column_config={
                    "Set": st.column_config.NumberColumn(
                        "Set",
                        disabled=True
                    ),

                    "Reps": st.column_config.NumberColumn(
                        "Reps",
                        min_value=1,
                        max_value=100,
                        step=1
                    ),

                    "Weight (kg)": st.column_config.NumberColumn(
                        "Weight (kg)",
                        min_value=0.0,
                        max_value=1000.0,
                        step=0.5
                    )
                },
                hide_index=True,
                use_container_width=True
            )

            # ------------------------------------------------
            # Exercise volume
            # ------------------------------------------------

            exercise_volume = (
                edited_data["Reps"]
                * edited_data["Weight (kg)"]
            ).sum()

            st.caption(
                f"Exercise volume: "
                f"{exercise_volume:.1f} kg"
            )

            # ------------------------------------------------
            # Add exercise
            # ------------------------------------------------

            if st.button("Add Exercise"):

                sets = []

                for _, row in edited_data.iterrows():

                    sets.append({
                        "set_number": int(row["Set"]),
                        "reps": int(row["Reps"]),
                        "weight": float(row["Weight (kg)"])
                    })

                st.session_state[
                    "workout_exercises"
                ].append({
                    "exercise": exercise,
                    "muscle": muscle_label,
                    "sets": sets
                })

                st.success(
                    f"✅ {exercise} added to workout!"
                )

    # ========================================================
    # CURRENT WORKOUT
    # ========================================================

    if st.session_state["workout_exercises"]:

        st.divider()

        st.subheader("Your Workout So Far")

        total_volume = 0

        for exercise_data in st.session_state[
            "workout_exercises"
        ]:

            st.markdown(
                f"### {exercise_data['exercise']}"
            )

            st.caption(
                f"Muscle: {exercise_data['muscle']}"
            )

            sets_df = pd.DataFrame(
                exercise_data["sets"]
            )

            sets_df.columns = [
                "Set",
                "Reps",
                "Weight (kg)"
            ]

            st.dataframe(
                sets_df,
                hide_index=True,
                use_container_width=True
            )

            exercise_volume = (
                sets_df["Reps"]
                * sets_df["Weight (kg)"]
            ).sum()

            st.caption(
                f"Exercise volume: "
                f"{exercise_volume:.1f} kg"
            )

            total_volume += exercise_volume

        st.metric(
            "Total Workout Volume",
            f"{total_volume:.1f} kg"
        )

        # ====================================================
        # SAVE WORKOUT
        # ====================================================

        if st.button("💾 Save Workout"):

            if not workout_name.strip():

                st.error(
                    "Please enter a workout name."
                )

            else:

                try:

                    workout_id = save_workout(
                        workout_name,
                        st.session_state[
                            "workout_exercises"
                        ]
                    )

                    st.success(
                        f"✅ Workout saved! "
                        f"Workout ID: {workout_id}"
                    )

                    # Clear current workout
                    st.session_state[
                        "workout_exercises"
                    ] = []

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not save workout: {e}"
                    )


# ============================================================
# WORKOUT HISTORY
# ============================================================

with history_tab:

    st.header("📚 Workout History")

    workouts = get_workouts()

    if workouts.empty:

        st.info(
            "No saved workouts yet."
        )

    else:

        # ----------------------------------------------------
        # Workout selector
        # ----------------------------------------------------

        workout_options = {
            f"{row['name']} — {row['created_at']}":
            row["id"]
            for _, row in workouts.iterrows()
        }

        selected_workout = st.selectbox(
            "Select a workout:",
            list(workout_options.keys())
        )

        selected_workout_id = workout_options[
            selected_workout
        ]

        # ----------------------------------------------------
        # Get workout
        # ----------------------------------------------------

        details = get_workout_details(
            selected_workout_id
        )

        if details.empty:

            st.warning(
                "This workout has no exercises."
            )

        else:

            st.subheader(
                details.iloc[0]["workout"]
            )

            st.caption(
                f"Created: "
                f"{details.iloc[0]['created_at']}"
            )

            total_volume = 0

            # ------------------------------------------------
            # Group exercises
            # ------------------------------------------------

            for exercise_id, exercise_df in details.groupby(
                "exercise_id"
            ):

                exercise_name = (
                    exercise_df.iloc[0]["exercise"]
                )

                muscle = (
                    exercise_df.iloc[0]["muscle"]
                )

                st.markdown(
                    f"### {exercise_name}"
                )

                st.caption(
                    f"Muscle: {muscle}"
                )

                display_df = exercise_df[
                    [
                        "set_number",
                        "reps",
                        "weight"
                    ]
                ].copy()

                display_df.columns = [
                    "Set",
                    "Reps",
                    "Weight (kg)"
                ]

                st.dataframe(
                    display_df,
                    hide_index=True,
                    use_container_width=True
                )

                exercise_volume = (
                    display_df["Reps"]
                    * display_df["Weight (kg)"]
                ).sum()

                st.caption(
                    f"Exercise volume: "
                    f"{exercise_volume:.1f} kg"
                )

                total_volume += exercise_volume

            # ------------------------------------------------
            # Total volume
            # ------------------------------------------------

            st.divider()

            st.metric(
                "Total Workout Volume",
                f"{total_volume:.1f} kg"
            )