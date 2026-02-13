"""
COMPREHENSIVE CONSTRAINT VERIFICATION
======================================
Checks ALL 7 constraints are satisfied in the final schedule
"""

import pandas as pd


def verify_all_constraints(schedule_df, params):
    """
    Verify all 7 constraints are satisfied
    
    Parameters:
    -----------
    schedule_df : pd.DataFrame
        The schedule dataframe from display_all_views
    params : dict
        Problem parameters
        
    Returns:
    --------
    bool : True if all constraints satisfied, False otherwise
    """
    
    print("\n" + "="*100)
    print("COMPREHENSIVE CONSTRAINT VERIFICATION")
    print("="*100)
    
    all_passed = True
    
    # ==========================================================================
    # CONSTRAINT 1: Each session scheduled exactly once (or twice for tutorials)
    # ==========================================================================
    
    print("\n" + "="*100)
    print("CONSTRAINT 1: Session Scheduling")
    print("="*100)
    
    violations = []
    
    for c in params['C']:
        for i in params['I'][c]:
            sessions = schedule_df[(schedule_df['Course'] == c) & (schedule_df['Session'] == i)]
            expected = 2 if params['Timeline'][c][i] == 'T' else 1
            actual = len(sessions)
            
            if actual != expected:
                violations.append({
                    'Course': c,
                    'Session': i,
                    'Type': params['Timeline'][c][i],
                    'Expected': expected,
                    'Actual': actual
                })
    
    if violations:
        print(f"❌ FAILED: {len(violations)} violations found")
        all_passed = False
        for v in violations[:5]:  # Show first 5
            print(f"   {v['Course']} Session {v['Session']} ({v['Type']}): Expected {v['Expected']} rooms, got {v['Actual']}")
    else:
        lectures = schedule_df[schedule_df['Type'] == 'C']
        tutorials = schedule_df[schedule_df['Type'] == 'T']
        print(f"✅ PASSED")
        print(f"   Lectures: {len(lectures)} sessions (1 room each)")
        print(f"   Tutorials: {len(tutorials)} sessions (should be pairs, 2 rooms each)")
    
    # ==========================================================================
    # CONSTRAINT 2: Room capacity ≥ 50% of students (25% for tutorials)
    # ==========================================================================
    
    print("\n" + "="*100)
    print("CONSTRAINT 2: Room Capacity")
    print("="*100)
    
    violations = []
    
    for _, session in schedule_df.iterrows():
        if session['Type'] == 'T':
            # Tutorial: each room needs 25% capacity (students split across 2 rooms)
            min_capacity = 0.25 * session['Students']
        else:
            # Lecture: needs 50% capacity
            min_capacity = 0.5 * session['Students']
        
        if session['Room_Capacity'] < min_capacity:
            violations.append({
                'Course': session['Course'],
                'Session': session['Session'],
                'Room': session['Room'],
                'Capacity': session['Room_Capacity'],
                'Required': min_capacity,
                'Students': session['Students']
            })
    
    if violations:
        print(f"❌ FAILED: {len(violations)} violations found")
        all_passed = False
        for v in violations[:5]:
            print(f"   {v['Course']} S{v['Session']} in {v['Room']}: Capacity {v['Capacity']}, need {v['Required']:.0f} ({v['Students']} students)")
    else:
        print(f"✅ PASSED")
        print(f"   All {len(schedule_df)} sessions have sufficient room capacity")
    
    # ==========================================================================
    # CONSTRAINT 3: No room double-booking
    # ==========================================================================
    
    print("\n" + "="*100)
    print("CONSTRAINT 3: No Room Double-Booking")
    print("="*100)
    
    violations = []
    
    for room in schedule_df['Room'].unique():
        room_schedule = schedule_df[schedule_df['Room'] == room]
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            for time in ['08:30-10:30', '11:00-13:00', '13:30-15:30', '16:00-18:00']:
                sessions = room_schedule[(room_schedule['Day'] == day) & (room_schedule['Time'] == time)]
                
                if len(sessions) > 1:
                    violations.append({
                        'Room': room,
                        'Day': day,
                        'Time': time,
                        'Courses': ', '.join(sessions['Course'].tolist())
                    })
    
    if violations:
        print(f"❌ FAILED: {len(violations)} conflicts found")
        all_passed = False
        for v in violations[:5]:
            print(f"   {v['Room']} on {v['Day']} at {v['Time']}: {v['Courses']}")
    else:
        print(f"✅ PASSED")
        print(f"   No room conflicts found across {len(schedule_df)} sessions")
    
    # ==========================================================================
    # CONSTRAINT 4: Lecturer unavailability
    # ==========================================================================
    
    print("\n" + "="*100)
    print("CONSTRAINT 4: Lecturer Unavailability")
    print("="*100)
    
    violations = []
    
    for lecturer, unavailable_days in params['U'].items():
        if unavailable_days:
            lecturer_schedule = schedule_df[schedule_df['Lecturer'] == lecturer]
            
            for day in unavailable_days:
                day_sessions = lecturer_schedule[lecturer_schedule['Day'] == day]
                
                if len(day_sessions) > 0:
                    for _, session in day_sessions.iterrows():
                        violations.append({
                            'Lecturer': lecturer,
                            'Day': day,
                            'Course': session['Course'],
                            'Session': session['Session'],
                            'Time': session['Time']
                        })
    
    if violations:
        print(f"❌ FAILED: {len(violations)} violations found")
        all_passed = False
        for v in violations[:5]:
            print(f"   {v['Lecturer']} teaching on {v['Day']} at {v['Time']}: {v['Course']} Session {v['Session']}")
    else:
        unavailable_count = sum(1 for days in params['U'].values() if days)
        print(f"✅ PASSED")
        print(f"   All {unavailable_count} lecturers with unavailability are respected")
    
    # ==========================================================================
    # CONSTRAINT 5: Lecturer no double-booking
    # ==========================================================================
    
    print("\n" + "="*100)
    print("CONSTRAINT 5: Lecturer No Double-Booking")
    print("="*100)
    
    violations = []
    
    for lecturer in schedule_df['Lecturer'].unique():
        lecturer_schedule = schedule_df[schedule_df['Lecturer'] == lecturer]
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            for time in ['08:30-10:30', '11:00-13:00', '13:30-15:30', '16:00-18:00']:
                sessions = lecturer_schedule[(lecturer_schedule['Day'] == day) & (lecturer_schedule['Time'] == time)]
                
                if len(sessions) > 1:
                    violations.append({
                        'Lecturer': lecturer,
                        'Day': day,
                        'Time': time,
                        'Courses': ', '.join(f"{s['Course']} S{s['Session']}" for _, s in sessions.iterrows())
                    })
    
    if violations:
        print(f"❌ FAILED: {len(violations)} conflicts found")
        all_passed = False
        for v in violations[:5]:
            print(f"   {v['Lecturer']} on {v['Day']} at {v['Time']}: {v['Courses']}")
    else:
        print(f"✅ PASSED")
        print(f"   No lecturer conflicts across {schedule_df['Lecturer'].nunique()} lecturers")
    
    # ==========================================================================
    # CONSTRAINT 6: Student no overlap
    # ==========================================================================
    
    print("\n" + "="*100)
    print("CONSTRAINT 6: Student No Overlap")
    print("="*100)
    
    violations = []
    
    for program in params['P']:
        program_courses = params['Courses'][program]
        program_schedule = schedule_df[schedule_df['Course'].isin(program_courses)]
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            for time in ['08:30-10:30', '11:00-13:00', '13:30-15:30', '16:00-18:00']:
                sessions = program_schedule[(program_schedule['Day'] == day) & (program_schedule['Time'] == time)]
                
                # Tutorials with 2 rooms at same time are OK
                unique_courses_sessions = sessions.drop_duplicates(subset=['Course', 'Session'])
                
                if len(unique_courses_sessions) > 1:
                    violations.append({
                        'Program': program,
                        'Day': day,
                        'Time': time,
                        'Courses': ', '.join(f"{s['Course']} S{s['Session']}" for _, s in unique_courses_sessions.iterrows())
                    })
    
    if violations:
        print(f"❌ FAILED: {len(violations)} conflicts found")
        all_passed = False
        for v in violations[:5]:
            print(f"   {v['Program']} on {v['Day']} at {v['Time']}: {v['Courses']}")
    else:
        print(f"✅ PASSED")
        print(f"   No student conflicts across {len(params['P'])} programs")
    
    # ==========================================================================
    # CONSTRAINT 7: Chronological ordering
    # ==========================================================================
    
    print("\n" + "="*100)
    print("CONSTRAINT 7: Chronological Ordering")
    print("="*100)
    
    violations = []
    
    day_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5}
    time_order = {'08:30-10:30': 1, '11:00-13:00': 2, '13:30-15:30': 3, '16:00-18:00': 4}
    
    for c in params['C']:
        course_schedule = schedule_df[schedule_df['Course'] == c].sort_values('Session')
        
        for i in range(len(params['I'][c]) - 1):
            session_i = course_schedule[course_schedule['Session'] == i]
            session_i_plus_1 = course_schedule[course_schedule['Session'] == i + 1]
            
            if len(session_i) > 0 and len(session_i_plus_1) > 0:
                # Get earliest time for session i (if tutorial has 2 rooms)
                time_i = min((day_order[row['Day']], time_order[row['Time']]) for _, row in session_i.iterrows())
                
                # Get earliest time for session i+1
                time_i_plus_1 = min((day_order[row['Day']], time_order[row['Time']]) for _, row in session_i_plus_1.iterrows())
                
                if time_i >= time_i_plus_1:
                    violations.append({
                        'Course': c,
                        'Session_i': i,
                        'Session_i+1': i + 1,
                        'Time_i': f"{session_i.iloc[0]['Day']} {session_i.iloc[0]['Time']}",
                        'Time_i+1': f"{session_i_plus_1.iloc[0]['Day']} {session_i_plus_1.iloc[0]['Time']}"
                    })
    
    if violations:
        print(f"❌ FAILED: {len(violations)} ordering violations found")
        all_passed = False
        for v in violations[:5]:
            print(f"   {v['Course']}: Session {v['Session_i']} at {v['Time_i']} NOT before Session {v['Session_i+1']} at {v['Time_i+1']}")
    else:
        print(f"✅ PASSED")
        print(f"   All {len(params['C'])} courses have sessions in correct chronological order")
    
    # ==========================================================================
    # SUMMARY
    # ==========================================================================
    
    print("\n" + "="*100)
    print("VERIFICATION SUMMARY")
    print("="*100)
    
    if all_passed:
        print("\n🎉 ALL CONSTRAINTS SATISFIED! 🎉")
        print("   The schedule is valid and meets all requirements.")
    else:
        print("\n⚠️  SOME CONSTRAINTS VIOLATED")
        print("   Review the violations above and check the model constraints.")
    
    print("="*100 + "\n")
    
    return all_passed


if __name__ == "__main__":
    print("""
    Comprehensive Constraint Verification
    ======================================
    
    Usage in notebook:
    
    %run verify_all_constraints.py
    all_passed = verify_all_constraints(schedule_df, params)
    """)
