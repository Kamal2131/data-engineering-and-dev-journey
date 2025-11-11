# 🔥 MINI PROJECT: STUDENT GRADE EVALUATOR


# ✅ Step-by-step approach
#
# Ask user: how many students
# Loop through each student
# Store them in a list of dicts
# Use a function to evaluate grade
# Print summary


def get_grade(marks : int):
    if marks >= 90 :
        return 'A'
    elif marks >= 80:
        return 'B'
    elif marks >= 70:
        return 'C'
    else :
        return 'D'

count = int(input("Enter How Many Students is there : "))

student = []
for _ in range(count):
    name = input("Enter Student Name : ")
    mark = float(input("Enter Student Mark : "))
    student.append({"name": name, "mark": mark})

print(student)

for s in student:
    grade = get_grade(int(s['mark']))
    print(f"{s['name']} Got Marks {s['mark']} : {grade}")
