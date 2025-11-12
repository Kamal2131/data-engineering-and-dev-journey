# 🧠 Features
#
#  Add student (name, marks, grade)
#  Save data to both CSV & JSON
#  Load and display all student records
#  Bonus: Use pandas to calculate average marks

import csv
import json
import pandas as pd

CSV_FILE = "students.csv"
JSON_FILE = "students.json"
FIELDNAMES = ["Name", "Marks", "Grade"]

# Add New Students Records
def add_student(name, marks, grade):
    student = {"Name": name, "Marks": marks, "Grade": grade}

    # Write To CSV
    with open(CSV_FILE, 'a', newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(student)

    # Write To JSON
    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(student)
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print("Student added successfully")

# Display Records
def show_students():
    try:
        df = pd.read_csv(CSV_FILE)
        # ensure Marks numeric before computing mean
        if "Marks" in df.columns:
            df["Marks"] = pd.to_numeric(df["Marks"], errors="coerce")
        print(df)
        if "Marks" in df.columns:
            print("\nAverage Marks:", df["Marks"].mean())
    except (FileNotFoundError, pd.errors.EmptyDataError):
        print("No records found.")
    except Exception as e:
        print("Error reading records:", e)

# CLI Menu
def main():
    try:
        while True:
            print("\n1. Add Student\n2. Show Students\n3. Exit")
            try:
                choice = input("Enter choice: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\nInterrupted! Exiting.")
                break

            if choice == "1":
                name = input("Name: ").strip()
                marks_input = input("Marks: ").strip()
                # guard: don't crash on bad marks
                try:
                    marks = int(marks_input)
                except ValueError:
                    print("Marks must be an integer. Try again.")
                    continue
                grade = input("Grade: ").strip()
                add_student(name, marks, grade)
            elif choice == "2":
                show_students()
            elif choice == "3":
                print("Goodbye 👋")
                break
            else:
                print("Invalid choice!")
    except KeyboardInterrupt:
        # fallback: if an interrupt bubbles up, exit cleanly
        print("\n\nInterrupted! Exiting.")

if __name__ == "__main__":
    main()
