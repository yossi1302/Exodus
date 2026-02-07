import pulp
print(f'PuLP {pulp.__version__} imported successfully')
prob = pulp.LpProblem('test', pulp.LpMaximize)
x = pulp.LpVariable('x', 0, 3)
prob += x
prob += x <= 2; prob.solve(pulp.PULP_CBC_CMD(msg=0)); print(f'Test optimization: status={pulp.LpStatus[prob.status]}, x={pulp.value(x)}')