"""
Minimal test to verify constraint logic works
This creates a tiny problem that SHOULD be feasible
"""

import pulp

def create_minimal_test():
    """
    Create the simplest possible test case:
    - 1 course with 2 sessions
    - 2 rooms
    - 2 days, 2 time slots
    - 1 lecturer (always available)
    - 1 program
    
    This MUST have a solution!
    """
    
    print("Creating minimal test case...")
    
    # Minimal parameters
    test_params = {
        'C': ['TEST_COURSE'],
        'R': ['ROOM_A', 'ROOM_B'],
        'D': [1, 2],  # 2 days
        'T': [1, 2],  # 2 time slots
        'L': ['TEST_PROF'],
        'P': ['TEST_PROGRAM'],
        
        'I': {'TEST_COURSE': [0, 1]},  # 2 sessions
        'Timeline': {'TEST_COURSE': ['C', 'T']},
        'Lecturer': {'TEST_COURSE': 'TEST_PROF'},
        'Cap': {'ROOM_A': 100, 'ROOM_B': 50},
        'U': {},  # No unavailability
        'Courses': {'TEST_PROGRAM': ['TEST_COURSE']},
        'students_per_course': {'TEST_COURSE': 80},
        'n': {'TEST_PROGRAM': 80}
    }
    
    # Create model
    model = pulp.LpProblem("Minimal_Test", pulp.LpMinimize)
    
    # Create variables
    x = pulp.LpVariable.dicts(
        "schedule",
        [(c, i, r, d, t)
         for c in test_params['C']
         for i in test_params['I'][c]
         for r in test_params['R']
         for d in test_params['D']
         for t in test_params['T']],
        cat='Binary'
    )
    
    print(f"Created {len(x)} variables")
    
    # Objective
    model += 0, "Feasibility"
    
    # CONSTRAINT 1: Each session scheduled once
    for c in test_params['C']:
        for i in test_params['I'][c]:
            model += (
                pulp.lpSum(
                    x[c, i, r, d, t]
                    for r in test_params['R']
                    for d in test_params['D']
                    for t in test_params['T']
                ) == 1,
                f"C1_{c}_i{i}"
            )
    print("✓ Constraint 1 added")
    
    # CONSTRAINT 2: Room capacity
    for c in test_params['C']:
        min_cap = 0.5 * test_params['students_per_course'][c]
        for i in test_params['I'][c]:
            for r in test_params['R']:
                if test_params['Cap'][r] >= min_cap:
                    for d in test_params['D']:
                        for t in test_params['T']:
                            model += (
                                x[c, i, r, d, t] * test_params['students_per_course'][c] 
                                <= 2 * test_params['Cap'][r],
                                f"C2_{c}_i{i}_{r}_d{d}_t{t}"
                            )
                else:
                    for d in test_params['D']:
                        for t in test_params['T']:
                            model += (
                                x[c, i, r, d, t] == 0,
                                f"C2_block_{c}_i{i}_{r}_d{d}_t{t}"
                            )
    print("✓ Constraint 2 added")
    
    # CONSTRAINT 7: Ordering (session 0 before session 1)
    for c in test_params['C']:
        time_s0 = pulp.lpSum(
            (5 * d + t) * x[c, 0, r, d, t]
            for r in test_params['R']
            for d in test_params['D']
            for t in test_params['T']
        )
        
        time_s1 = pulp.lpSum(
            (5 * d + t) * x[c, 1, r, d, t]
            for r in test_params['R']
            for d in test_params['D']
            for t in test_params['T']
        )
        
        model += (
            time_s0 + 1 <= time_s1,
            f"C7_{c}_ordering"
        )
    print("✓ Constraint 7 added")
    
    # Solve
    print("\nSolving minimal test...")
    status = model.solve(pulp.PULP_CBC_CMD(msg=0))
    
    print(f"\nResult: {pulp.LpStatus[status]}")
    
    if status == pulp.LpStatusOptimal:
        print("\n✅ MINIMAL TEST PASSED!")
        print("\nSchedule found:")
        for (c, i, r, d, t), var in x.items():
            if var.varValue == 1:
                print(f"  Session {i}: Day {d}, Slot {t}, Room {r}")
        return True
    else:
        print("\n❌ MINIMAL TEST FAILED - Basic constraint logic is broken!")
        return False


if __name__ == "__main__":
    create_minimal_test()
