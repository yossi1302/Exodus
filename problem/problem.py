import pulp
from pulp.apis.cuopt_api import LpBinary

# 1. Create the problem
model = pulp.LpProblem("Model_Name", pulp.LpMaximize)  # or LpMinimize

# 2. Define decision variables

ROOMS = range(200)
COURSES = range(3)  # since courses == 3

x = pulp.LpVariable.dicts("x", (ROOMS, COURSES), cat="Binary")

lectures = pulp.LpVariable("lectures", lowBound=6)
tutorials = pulp.LpVariable("tutorials", lowBound=3)
courses = pulp.LpVariable("courses", lowBound=2)
total_required_rooms = lectures + tutorials * 3

# 3. Objective function
model += pulp.lpSum(x[r][c] for r in ROOMS for c in COURSES), "Maximize_Rooms"

# 4. Constraints
for r in ROOMS:
    model += pulp.lpSum(x[r][c] for c in COURSES) <= 1
model += tutorials == lectures / 2
model += lectures == 6 * courses
model += courses == 3  # get this value from json
model += pulp.lpSum(x[r][c] for r in ROOMS for c in COURSES) == total_required_rooms

# 5. Solve
model.solve()

# 6. Output results
print("Status:", pulp.LpStatus[model.status])
print("lectures =", pulp.value(lectures))
print("tutorials =", pulp.value(tutorials))
course_labels = {0: "A", 1: "B", 2: "C"}

for r in ROOMS:
    for c in COURSES:
        if pulp.value(x[r][c]) == 1:
            print(f"Room {r}: Course {course_labels[c]}")
