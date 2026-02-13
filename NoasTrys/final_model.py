"""
FINAL COURSE SCHEDULING MODEL
==============================
Clean implementation with all required constraints and optimization objectives.

Features:
1. Tutorials require 2 rooms (can be at different times, but same time is preferred)
2. Lecturer unavailability WORKING
3. Penalty for 08:30 lectures (but not tutorials)
4. FIXED chronological ordering
"""

import pulp


def create_optimized_model(params):
    """
    Create the complete course scheduling model with all constraints and objectives
    
    Parameters:
    -----------
    params : dict
        All problem parameters from load_parameters.py
        
    Returns:
    --------
    model : pulp.LpProblem
        The optimization model
    x : dict
        Decision variables x[c,i,r,d,t]
    y : dict
        Helper variables y[c,i,d,t] (1 if tutorial session i of course c on day d at time t)
    """
    
    print("\n" + "="*80)
    print("BUILDING OPTIMIZED COURSE SCHEDULING MODEL")
    print("="*80)
    
    # ==========================================================================
    # DECISION VARIABLES
    # ==========================================================================
    
    model = pulp.LpProblem("Course_Scheduling_Optimized", pulp.LpMinimize)
    
    # Main variable: x[c,i,r,d,t] = 1 if session i of course c in room r on day d at time t
    x = pulp.LpVariable.dicts(
        "schedule",
        [(c, i, r, d, t)
         for c in params['C']
         for i in params['I'][c]
         for r in params['R']
         for d in params['D']
         for t in params['T']],
        cat='Binary'
    )
    
    # Helper variable: y[c,i,d,t] = 1 if tutorial session i of course c is scheduled on day d at time t
    # (regardless of which rooms)
    y = pulp.LpVariable.dicts(
        "tutorial_time",
        [(c, i, d, t)
         for c in params['C']
         for i in params['I'][c]
         if params['Timeline'][c][i] == 'T'  # Only for tutorials
         for d in params['D']
         for t in params['T']],
        cat='Binary'
    )
    
    print(f"✅ Created {len(x)} main decision variables")
    print(f"✅ Created {len(y)} tutorial timing variables")
    
    # ==========================================================================
    # OBJECTIVE FUNCTION
    # ==========================================================================
    
    # Minimize:
    # 1. Early morning lectures (08:30 slot, but NOT tutorials) - weight 100
    # 2. Tutorial room splits (tutorials not at same time) - weight 10
    
    early_morning_penalty = pulp.lpSum(
        100 * x[c, i, r, d, 1]  # time slot 1 (08:30)
        for c in params['C']
        for i in params['I'][c]
        if params['Timeline'][c][i] == 'C'  # Only lectures (C), not tutorials (T)
        for r in params['R']
        for d in params['D']
    )
    
    # For tutorials requiring 2 rooms: penalize if they're at different times
    # If both rooms at same time: no penalty
    # If rooms at different times: penalty
    tutorial_split_penalty = 0
    
    for c in params['C']:
        for i in params['I'][c]:
            if params['Timeline'][c][i] == 'T':  # Is a tutorial
                # Penalty if y[c,i,d,t] = 1 for more than one (d,t) combination
                # This happens when rooms are scheduled at different times
                tutorial_split_penalty += 10 * pulp.lpSum(
                    y[c, i, d, t]
                    for d in params['D']
                    for t in params['T']
                )
                # We want this sum to be exactly 1 (all rooms at same time)
                # If it's 2, that means 2 different time slots were used
    
    model += early_morning_penalty + tutorial_split_penalty, "Minimize_Penalties"
    
    print("✅ Objective function set: minimize early lectures + tutorial splits")
    
    # ==========================================================================
    # CONSTRAINTS
    # ==========================================================================
    
    # --------------------------------------------------------------------------
    # CONSTRAINT 1: Each session scheduled exactly once (or twice for tutorials)
    # --------------------------------------------------------------------------
    
    for c in params['C']:
        for i in params['I'][c]:
            if params['Timeline'][c][i] == 'T':  # Tutorial needs 2 rooms
                model += (
                    pulp.lpSum(
                        x[c, i, r, d, t]
                        for r in params['R']
                        for d in params['D']
                        for t in params['T']
                    ) == 2,  # Exactly 2 rooms!
                    f"C1_Tutorial_{c}_i{i}_needs_2_rooms"
                )
            else:  # Lecture needs 1 room
                model += (
                    pulp.lpSum(
                        x[c, i, r, d, t]
                        for r in params['R']
                        for d in params['D']
                        for t in params['T']
                    ) == 1,
                    f"C1_Lecture_{c}_i{i}_needs_1_room"
                )
    
    print("✅ Constraint 1: Sessions scheduled (tutorials get 2 rooms)")
    
    # Link y variables to x for tutorials
    for c in params['C']:
        for i in params['I'][c]:
            if params['Timeline'][c][i] == 'T':
                for d in params['D']:
                    for t in params['T']:
                        # y[c,i,d,t] = 1 if ANY room is used for this tutorial at this time
                        for r in params['R']:
                            model += (
                                y[c, i, d, t] >= x[c, i, r, d, t],
                                f"Link_y_{c}_i{i}_r{r}_d{d}_t{t}"
                            )
                        
                        # y[c,i,d,t] <= sum of all rooms at this time (if 2 rooms used, y=1)
                        model += (
                            2 * y[c, i, d, t] >= pulp.lpSum(
                                x[c, i, r, d, t] for r in params['R']
                            ),
                            f"Link_y_sum_{c}_i{i}_d{d}_t{t}"
                        )
    
    print("✅ Linked tutorial timing variables")
    
    # --------------------------------------------------------------------------
    # CONSTRAINT 2: Room capacity ≥ 50% of students
    # --------------------------------------------------------------------------
    
    for c in params['C']:
        for i in params['I'][c]:
            # For tutorials, we split students across 2 rooms, so each needs 25% capacity
            if params['Timeline'][c][i] == 'T':
                min_capacity = 0.25 * params['students_per_course'][c]
            else:
                min_capacity = 0.5 * params['students_per_course'][c]
            
            for r in params['R']:
                if params['Cap'][r] >= min_capacity:
                    for d in params['D']:
                        for t in params['T']:
                            model += (
                                x[c, i, r, d, t] * params['students_per_course'][c] <= 2 * params['Cap'][r],
                                f"C2_Capacity_{c}_i{i}_r{r}_d{d}_t{t}"
                            )
                else:
                    for d in params['D']:
                        for t in params['T']:
                            model += (
                                x[c, i, r, d, t] == 0,
                                f"C2_TooSmall_{c}_i{i}_r{r}_d{d}_t{t}"
                            )
    
    print("✅ Constraint 2: Room capacity requirements")
    
    # --------------------------------------------------------------------------
    # CONSTRAINT 3: No room double-booking
    # --------------------------------------------------------------------------
    
    for r in params['R']:
        for d in params['D']:
            for t in params['T']:
                model += (
                    pulp.lpSum(
                        x[c, i, r, d, t]
                        for c in params['C']
                        for i in params['I'][c]
                    ) <= 1,
                    f"C3_NoDoubleBook_r{r}_d{d}_t{t}"
                )
    
    print("✅ Constraint 3: No room double-booking")
    
    # --------------------------------------------------------------------------
    # CONSTRAINT 4: Lecturer unavailability - FIXED!
    # --------------------------------------------------------------------------
    
    DAY_NAMES = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday'}
    constraint_count = 0
    
    for c in params['C']:
        lecturer = params['Lecturer'][c]
        unavailable_days = params['U'].get(lecturer, [])
        
        for i in params['I'][c]:
            for d in params['D']:
                day_name = DAY_NAMES[d]
                if day_name in unavailable_days:
                    for t in params['T']:
                        model += (
                            pulp.lpSum(
                                x[c, i, r, d, t]
                                for r in params['R']
                            ) == 0,
                            f"C4_Unavailable_{c}_i{i}_{lecturer}_d{d}_t{t}"
                        )
                        constraint_count += 1
    
    print(f"✅ Constraint 4: Lecturer unavailability ({constraint_count} constraints)")
    
    if constraint_count == 0:
        print("  ⚠️  WARNING: No unavailability constraints added - check U parameter!")
    
    # --------------------------------------------------------------------------
    # CONSTRAINT 5: Lecturer no double-booking
    # --------------------------------------------------------------------------
    
    for l in params['L']:
        courses_by_lecturer = [c for c in params['C'] if params['Lecturer'][c] == l]
        
        for d in params['D']:
            for t in params['T']:
                model += (
                    pulp.lpSum(
                        x[c, i, r, d, t]
                        for c in courses_by_lecturer
                        for i in params['I'][c]
                        for r in params['R']
                    ) <= 1,
                    f"C5_NoDoubleTeach_{l}_d{d}_t{t}"
                )
    
    print("✅ Constraint 5: Lecturer no double-booking")
    
    # --------------------------------------------------------------------------
    # CONSTRAINT 6: Student no overlap
    # --------------------------------------------------------------------------
    
    for p in params['P']:
        courses = params['Courses'][p]
        
        for d in params['D']:
            for t in params['T']:
                model += (
                    pulp.lpSum(
                        x[c, i, r, d, t]
                        for c in courses
                        for i in params['I'][c]
                        for r in params['R']
                    ) <= 1,
                    f"C6_NoStudentOverlap_{p}_d{d}_t{t}"
                )
    
    print("✅ Constraint 6: Student no overlap")
    
    # --------------------------------------------------------------------------
    # CONSTRAINT 7: Chronological ordering - FIXED VERSION
    # --------------------------------------------------------------------------
    
    print("⏳ Adding Constraint 7: Chronological ordering (this may take a moment)...")
    
    constraint_count_c7 = 0
    
    for c in params['C']:
        for i in range(len(params['I'][c]) - 1):
            # Session i must come STRICTLY BEFORE session i+1
            # This means: ALL rooms of session i must be before ALL rooms of session i+1
            
            for r_i in params['R']:
                for d_i in params['D']:
                    for t_i in params['T']:
                        # If session i is in room r_i on day d_i at time t_i...
                        
                        for r_j in params['R']:
                            for d_j in params['D']:
                                for t_j in params['T']:
                                    # Then session i+1 CANNOT be scheduled at or before this time
                                    
                                    time_i = 5 * d_i + t_i
                                    time_j = 5 * d_j + t_j
                                    
                                    if time_j <= time_i:
                                        # If session i+1 would be at same time or earlier, prevent it
                                        model += (
                                            x[c, i, r_i, d_i, t_i] + x[c, i + 1, r_j, d_j, t_j] <= 1,
                                            f"C7_Order_{c}_i{i}_d{d_i}t{t_i}_before_i{i+1}_d{d_j}t{t_j}"
                                        )
                                        constraint_count_c7 += 1
    
    print(f"✅ Constraint 7: Chronological ordering ({constraint_count_c7} constraints added)")
    
    # --------------------------------------------------------------------------
    # MODEL SUMMARY
    # --------------------------------------------------------------------------
    
    print("\n" + "="*80)
    print("MODEL READY TO SOLVE")
    print("="*80)
    print(f"Variables: {len(x) + len(y)}")
    print(f"Constraints: ~{len(model.constraints)}")
    print("="*80 + "\n")
    
    return model, x, y


if __name__ == "__main__":
    print("""
    Final Course Scheduling Model
    ==============================
    
    Usage in notebook:
    
    # Load parameters
    %run load_parameters.py
    
    # Create and solve model
    %run final_model.py
    model, x, y = create_optimized_model(params)
    status = model.solve(pulp.PULP_CBC_CMD(msg=1))
    
    print(f"Status: {pulp.LpStatus[status]}")
    
    # Visualize if successful
    if status == pulp.LpStatusOptimal:
        %run visualize_schedule.py
        schedule_df = display_all_views(x, params)
    """)
