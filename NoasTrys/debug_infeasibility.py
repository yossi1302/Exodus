"""
Debugging script to identify why the model is infeasible
"""

def diagnose_infeasibility(params):
    """
    Check for common issues that cause infeasibility
    """
    print("\n" + "="*80)
    print("INFEASIBILITY DIAGNOSIS")
    print("="*80)
    
    # 1. Check room capacity constraints
    print("\n1. ROOM CAPACITY CHECK")
    print("-" * 80)
    
    for c in params['C']:
        students = params['students_per_course'][c]
        min_capacity_needed = 0.5 * students
        
        valid_rooms = [r for r in params['R'] if params['Cap'][r] >= min_capacity_needed]
        
        print(f"{c}: {students} students (need ≥{min_capacity_needed:.0f} capacity)")
        print(f"  Valid rooms: {valid_rooms}")
        
        if len(valid_rooms) == 0:
            print(f"  ❌ PROBLEM: No room big enough for {c}!")
        elif len(valid_rooms) < 3:
            print(f"  ⚠️  WARNING: Only {len(valid_rooms)} room(s) available")
    
    # 2. Check lecturer unavailability
    print("\n2. LECTURER AVAILABILITY CHECK")
    print("-" * 80)
    
    DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for l in params['L']:
        unavailable = params['U'].get(l, [])
        courses_taught = [c for c in params['C'] if params['Lecturer'][c] == l]
        
        if len(courses_taught) > 0:
            available_days = [d for d in DAY_NAMES if d not in unavailable]
            total_sessions = sum(len(params['I'][c]) for c in courses_taught)
            
            print(f"{l}:")
            print(f"  Teaches: {courses_taught} ({total_sessions} sessions total)")
            print(f"  Available: {len(available_days)} days {available_days}")
            print(f"  Unavailable: {unavailable}")
            
            # Check if enough slots
            available_slots = len(available_days) * 4  # 4 time slots per day
            if total_sessions > available_slots:
                print(f"  ❌ PROBLEM: {total_sessions} sessions but only {available_slots} available slots!")
    
    # 3. Check for Tom specifically (teaches 2 courses)
    print("\n3. MULTI-COURSE LECTURER CHECK (Tom)")
    print("-" * 80)
    
    tom_courses = [c for c in params['C'] if params['Lecturer'][c] == 'Tom']
    if len(tom_courses) > 1:
        total_sessions = sum(len(params['I'][c]) for c in tom_courses)
        print(f"Tom teaches {len(tom_courses)} courses: {tom_courses}")
        print(f"Total sessions: {total_sessions}")
        print(f"Available time periods: 20 (5 days × 4 slots)")
        
        if total_sessions > 20:
            print(f"❌ PROBLEM: Tom has {total_sessions} sessions but only 20 time periods!")
        else:
            print(f"✅ OK: {total_sessions} sessions fits in 20 time periods")
    
    # 4. Check program conflicts
    print("\n4. PROGRAM OVERLAP CHECK")
    print("-" * 80)
    
    for p in params['P']:
        courses = params['Courses'][p]
        total_sessions = sum(len(params['I'][c]) for c in courses)
        
        print(f"{p}: {len(courses)} courses, {total_sessions} total sessions")
        
        if total_sessions > 20:
            print(f"  ❌ PROBLEM: {total_sessions} sessions but only 20 time slots!")
        else:
            print(f"  ✅ OK: {total_sessions} sessions fits in 20 time slots")
    
    # 5. Check if courses have 0 students
    print("\n5. ZERO-STUDENT COURSES CHECK")
    print("-" * 80)
    
    zero_student_courses = [c for c in params['C'] if params['students_per_course'][c] == 0]
    if zero_student_courses:
        print(f"⚠️  Found {len(zero_student_courses)} courses with 0 students:")
        for c in zero_student_courses:
            print(f"  - {c}")
        print("These courses might cause issues if they're required in a program.")
    else:
        print("✅ All courses have students")
    
    # 6. Overall capacity check
    print("\n6. OVERALL CAPACITY CHECK")
    print("-" * 80)
    
    total_sessions = sum(len(params['I'][c]) for c in params['C'])
    total_time_slots = len(params['D']) * len(params['T'])
    total_capacity = total_time_slots * len(params['R'])
    
    print(f"Total sessions to schedule: {total_sessions}")
    print(f"Total capacity (time slots × rooms): {total_time_slots} × {len(params['R'])} = {total_capacity}")
    print(f"Utilization: {100 * total_sessions / total_capacity:.1f}%")
    
    if total_sessions > total_capacity:
        print("❌ PROBLEM: More sessions than capacity!")
    else:
        print("✅ OK: Enough capacity")
    
    print("\n" + "="*80)
    print("DIAGNOSIS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    print("This script should be run from a notebook after loading parameters:")
    print("  %run load_parameters.py")
    print("  %run debug_infeasibility.py")
    print("  diagnose_infeasibility(params)")
