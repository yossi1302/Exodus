"""
Course Scheduling Parameter Loader
Load all parameters from JSON files into Python data structures
"""

import json
from datetime import datetime
from typing import Dict, List, Set, Tuple

# ============================================================================
# LOAD JSON FILES
# ============================================================================

def load_json_files():
    """Load all JSON configuration files"""
    
    with open('classrooms.json', 'r') as f:
        classrooms_data = json.load(f)
    
    with open('programs.json', 'r') as f:
        programs_data = json.load(f)
    
    with open('lecturers.json', 'r') as f:
        lecturers_data = json.load(f)
    
    with open('courses.json', 'r') as f:
        courses_data = json.load(f)
    
    return classrooms_data, programs_data, lecturers_data, courses_data


# ============================================================================
# DEFINE CONSTANTS
# ============================================================================

# Days: Monday=1, Tuesday=2, Wednesday=3, Thursday=4, Friday=5
DAYS = [1, 2, 3, 4, 5]
DAY_NAMES = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday'}

# Time slots: 1=08:30-10:30, 2=11:00-13:00, 3=13:30-15:30, 4=16:00-18:00
TIME_SLOTS = [1, 2, 3, 4]
TIME_SLOT_NAMES = {
    1: '08:30-10:30',
    2: '11:00-13:00',
    3: '13:30-15:30',
    4: '16:00-18:00'
}

# Week to schedule (you can modify these dates for your actual week)
WEEK_START_DATE = "2025-10-27"  # Monday
WEEK_DATES = {
    1: "2025-10-27",  # Monday
    2: "2025-10-28",  # Tuesday
    3: "2025-10-29",  # Wednesday
    4: "2025-10-30",  # Thursday
    5: "2025-10-31",  # Friday
}


# ============================================================================
# PROCESS PARAMETERS
# ============================================================================

def process_parameters():
    """
    Process all JSON data into clean Python data structures
    Returns all sets and parameters needed for the optimization model
    """
    
    # Load raw data
    classrooms_data, programs_data, lecturers_data, courses_data = load_json_files()
    
    # ========================================================================
    # SETS
    # ========================================================================
    
    # P: Set of programs
    P = list(programs_data.keys())
    print(f"Programs (P): {P}")
    
    # C: Set of courses
    C = list(courses_data.keys())
    print(f"Courses (C): {C}")
    
    # R: Set of rooms
    R = list(classrooms_data.keys())
    print(f"Rooms (R): {R}")
    
    # L: Set of lecturers
    L = list(lecturers_data.keys())
    print(f"Lecturers (L): {L}")
    
    # D: Set of days (already defined as constant)
    D = DAYS
    
    # T: Set of time slots (already defined as constant)
    T = TIME_SLOTS
    
    
    # ========================================================================
    # PARAMETERS - Program Data
    # ========================================================================
    
    # n_p: Number of students in program p
    n = {}
    for program in P:
        n[program] = programs_data[program]['size']
    print(f"\nStudent counts (n_p): {n}")
    
    # Courses_p: Set of courses for each program
    Courses = {}
    for program in P:
        Courses[program] = programs_data[program]['courses']
    print(f"\nCourses per program (Courses_p): {Courses}")
    
    
    # ========================================================================
    # PARAMETERS - Course Data
    # ========================================================================
    
    # Timeline_c: Session timeline for each course
    Timeline = {}
    for course in C:
        Timeline[course] = courses_data[course]['timeline']
    print(f"\nCourse timelines (Timeline_c): {Timeline}")
    
    # I_c: Session indices for each course (derived from timeline)
    I = {}
    for course in C:
        I[course] = list(range(len(Timeline[course])))
    print(f"\nSession indices (I_c): {I}")
    
    # Lecturer_c: Lecturer assigned to each course
    Lecturer = {}
    for course in C:
        # Note: lecturers.json has it as a list, take first element
        Lecturer[course] = courses_data[course]['lecturers'][0]
    print(f"\nCourse lecturers (Lecturer_c): {Lecturer}")
    
    
    # ========================================================================
    # PARAMETERS - Room Data
    # ========================================================================
    
    # Cap_r: Capacity of each room
    Cap = classrooms_data
    print(f"\nRoom capacities (Cap_r): {Cap}")
    
    
    # ========================================================================
    # PARAMETERS - Lecturer Availability
    # ========================================================================
    
    # U_l_d: Binary parameter - 1 if lecturer l is unavailable on day d
    U = {}
    for lecturer in L:
        for day in D:
            day_date = WEEK_DATES[day]
            if day_date in lecturers_data[lecturer]['unavailable']:
                U[lecturer, day] = 1
            else:
                U[lecturer, day] = 0
    
    print(f"\nLecturer unavailability (U_l,d):")
    for lecturer in L:
        unavailable_days = [DAY_NAMES[d] for d in D if U[lecturer, d] == 1]
        if unavailable_days:
            print(f"  {lecturer}: {unavailable_days}")
    
    
    # ========================================================================
    # DERIVED PARAMETERS
    # ========================================================================
    
    # Total students taking each course (sum across all programs)
    students_per_course = {}
    for course in C:
        total = 0
        for program in P:
            if course in Courses[program]:
                total += n[program]
        students_per_course[course] = total
    
    print(f"\nTotal students per course: {students_per_course}")
    
    
    # ========================================================================
    # RETURN ALL PARAMETERS
    # ========================================================================
    
    parameters = {
        # Sets
        'P': P,  # Programs
        'C': C,  # Courses
        'R': R,  # Rooms
        'L': L,  # Lecturers
        'D': D,  # Days
        'T': T,  # Time slots
        
        # Parameters - Program
        'n': n,  # Student count per program
        'Courses': Courses,  # Courses per program
        
        # Parameters - Course
        'Timeline': Timeline,  # Session timeline per course
        'I': I,  # Session indices per course
        'Lecturer': Lecturer,  # Lecturer per course
        
        # Parameters - Room
        'Cap': Cap,  # Room capacity
        
        # Parameters - Lecturer
        'U': U,  # Lecturer unavailability
        
        # Derived parameters
        'students_per_course': students_per_course,
        
        # Constants
        'DAY_NAMES': DAY_NAMES,
        'TIME_SLOT_NAMES': TIME_SLOT_NAMES,
        'WEEK_DATES': WEEK_DATES,
    }
    
    return parameters


# ============================================================================
# HELPER FUNCTIONS FOR DISPLAY
# ============================================================================

def print_summary(params):
    """Print a nice summary of all parameters"""
    
    print("\n" + "="*80)
    print("COURSE SCHEDULING PARAMETER SUMMARY")
    print("="*80)
    
    print(f"\n📅 SCHEDULING WEEK: {WEEK_START_DATE} to {WEEK_DATES[5]}")
    print(f"   Days: {len(params['D'])} days (Monday-Friday)")
    print(f"   Time slots per day: {len(params['T'])} slots")
    
    print(f"\n🎓 PROGRAMS: {len(params['P'])} programs")
    for p in params['P']:
        print(f"   {p}: {params['n'][p]} students, {len(params['Courses'][p])} courses")
    
    print(f"\n📚 COURSES: {len(params['C'])} courses")
    for c in params['C']:
        sessions = len(params['Timeline'][c])
        lecturer = params['Lecturer'][c]
        students = params['students_per_course'][c]
        print(f"   {c}: {sessions} sessions, taught by {lecturer}, {students} students")
    
    print(f"\n🏫 ROOMS: {len(params['R'])} rooms")
    for r in params['R']:
        print(f"   {r}: capacity {params['Cap'][r]}")
    
    print(f"\n👨‍🏫 LECTURERS: {len(params['L'])} lecturers")
    for l in params['L']:
        unavailable = [params['DAY_NAMES'][d] for d in params['D'] if params['U'][l, d] == 1]
        if unavailable:
            print(f"   {l}: unavailable on {', '.join(unavailable)}")
        else:
            print(f"   {l}: available all week")
    
    print("\n" + "="*80)


def check_data_integrity(params):
    """Check for potential issues in the data"""
    
    print("\n" + "="*80)
    print("DATA INTEGRITY CHECKS")
    print("="*80)
    
    issues = []
    
    # Check if any course has more students than largest room
    max_room_capacity = max(params['Cap'].values())
    for course in params['C']:
        min_required = 0.5 * params['students_per_course'][course]
        if min_required > max_room_capacity:
            issues.append(f"⚠️  Course {course} needs {min_required} seats (50% of {params['students_per_course'][course]}), but largest room has {max_room_capacity}")
    
    # Check if any lecturer is assigned to multiple courses
    lecturer_courses = {}
    for course in params['C']:
        lect = params['Lecturer'][course]
        if lect not in lecturer_courses:
            lecturer_courses[lect] = []
        lecturer_courses[lect].append(course)
    
    for lect, courses in lecturer_courses.items():
        if len(courses) > 1:
            print(f"ℹ️  Lecturer {lect} teaches {len(courses)} courses: {courses}")
    
    # Check total sessions to schedule
    total_sessions = sum(len(params['Timeline'][c]) for c in params['C'])
    total_slots = len(params['D']) * len(params['T'])
    print(f"\n📊 Total sessions to schedule: {total_sessions}")
    print(f"📊 Total available slots: {total_slots} ({len(params['D'])} days × {len(params['T'])} slots)")
    print(f"📊 Slot utilization: {total_sessions/total_slots*100:.1f}%")
    
    if issues:
        print("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ No data integrity issues found!")
    
    print("="*80)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Load and process all parameters
    params = process_parameters()
    
    # Print summary
    print_summary(params)
    
    # Check data integrity
    check_data_integrity(params)
    
    print("\n✅ All parameters loaded successfully!")
    print("   Use 'params' dictionary to access all data for your PuLP model")


# ============================================================================
# JUPYTER NOTEBOOK CONVENIENCE FUNCTION
# ============================================================================

def load_all_parameters():
    """
    Convenience function for Jupyter notebooks
    
    Usage:
        from load_parameters import load_all_parameters
        params = load_all_parameters()
    """
    params = process_parameters()
    print_summary(params)
    check_data_integrity(params)
    return params
