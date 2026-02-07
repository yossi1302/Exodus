import pulp
from pulp.apis.cuopt_api import LpBinary

# 1. Create the problem
model = pulp.LpProblem("Model_Name", pulp.LpMaximize)  # or LpMinimize

# 2. Define decision variables
rooms = pulp.LpVariable.dicts("rooms", range(10), lowBound=0, upBound=20, cat="Integer")

x = pulp.LpVariable("x", cat=LpBinary)
y = pulp.LpVariable("y", lowBound=0)

# 3. Objective function
model += pulp.lpSum(rooms.values()), "Maximize_Total_Rooms"

# 4. Constraints
model += x + y <= 10
model += x <= 6

# 5. Solve
model.solve()

# 6. Output results
print("Status:", pulp.LpStatus[model.status])
print("x =", pulp.value(x))
print("y =", pulp.value(y))
print("Maximum rooms =", pulp.value(model.objective))
