"""
FSP Course Scheduler - PuLP-based Linear Programming
Implements ONLY the 10 specified hard constraints
"""

import pulp
import json
from typing import Dict, List, Any
from datetime import datetime

# Constants
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']  # 5 weekdays
TIMESLOTS = ['08:30', '11:00', '13:30', '16:00']  # 4 slots per day
WEEKS = 1  # Only schedule for one week (27/10/2025)


def load_input_files():
    """Load all input JSON files"""
    with open('static/json_inputs_period/courses.json', 'r') as f:
        courses = json.load(f)
    
    with open('static/json_inputs_period/lecturers.json', 'r') as f:
        lecturers = json.load(f)
    
    with open('static/json_inputs_period/programs.json', 'r') as f:
        programs = json.load(f)
    
    with open('static/json_inputs_static/classrooms.json', 'r') as f:
        classrooms = json.load(f)
    
    return courses, lecturers, programs, classrooms


def generate_schedule(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to generate schedule using PuLP"""
    print("Starting schedule generation with PuLP...")
    
    # Load from files
    courses_raw, lecturers, programs, classrooms = load_input_files()
    
    # Convert course format
    courses_dict = {}
    for course_code, course_data in courses_raw.items():
        timeline = course_data['timeline']
        lectures = timeline.count('C')
        tutorials = timeline.count('T')
        
        courses_dict[course_code] = {
            'code': course_code,
            'name': course_data['name'],
            'lectures': lectures,
            'tutorials': tutorials,
            'lecturers': course_data['lecturers']
        }
    
    # Solve with PuLP
    schedule = solve_with_pulp(courses_dict, lecturers, programs, classrooms, 
                               input_data.get('metadata', {}))
    
    print("Schedule generation complete!")
    return schedule


def solve_with_pulp(courses_dict, teachers, programs, classrooms, metadata):
    """
    PuLP solver implementing the 10 hard constraints:
    1. Teacher can only teach one course at the same time
    2. Required class hours for each course are met until the end of the week
    3. No scheduling at unavailable time for teachers
    4. At least 0.5 of students fit in room
    5. 4 lecture slots in a day
    6. 5 weekdays for lectures
    7. At a time slot student group has one or none lectures
    8. Flow: lecture before tutorial
    9. No room used by 2 classes
    10. Each lecture/tutorial only happens once
    """
    
    print("Creating PuLP model with 10 hard constraints...")
    
    prob = pulp.LpProblem("CourseScheduling", pulp.LpMinimize)
    
    # Build list of all sessions to schedule
    all_sessions = []
    
    for course_code, course_data in courses_dict.items():
        # Find which program(s) use this course
        program_name = None
        program_size = 0
        for prog_name, prog_data in programs.items():
            if course_code in prog_data['courses']:
                program_name = prog_name
                program_size = prog_data['size']
                break
        
        teacher = course_data['lecturers'][0] if course_data['lecturers'] else None
        
        # Schedule lectures (2 per week for 7 weeks)
        for week in range(WEEKS):
            for lec_num in range(course_data['lectures']):
                all_sessions.append({
                    'id': f"{course_code}_L{lec_num}_w{week}",
                    'course': course_code,
                    'type': 'lecture',
                    'week': week,
                    'program': program_name,
                    'teacher': teacher,
                    'capacity_needed': program_size
                })
        
        # Schedule tutorials (1 per week, 4 groups)
        if course_data['tutorials'] > 0:
            for week in range(WEEKS):
                for group in range(4):
                    all_sessions.append({
                        'id': f"{course_code}_T_g{group}_w{week}",
                        'course': course_code,
                        'type': 'tutorial',
                        'week': week,
                        'program': program_name,
                        'teacher': teacher,
                        'capacity_needed': program_size / 4,  # Split into groups
                        'group': group
                    })
    
    # Decision variables: X[session_id, day, time, room] = 1 if scheduled
    variables = {}
    
    for session in all_sessions:
        for day_idx, day in enumerate(DAYS):
            for time_idx, time in enumerate(TIMESLOTS):
                for room, capacity in classrooms.items():
                    # CONSTRAINT 4: At least 0.5 of students fit in room
                    if capacity >= session['capacity_needed'] * 0.5:
                        var_name = f"{session['id']}_d{day_idx}_t{time_idx}_{room}"
                        variables[var_name] = pulp.LpVariable(var_name, cat='Binary')
    
    print(f"Created {len(variables)} variables for {len(all_sessions)} sessions")
    
    # NEW CONSTRAINT: All 4 tutorial groups must be at same time/day
    print("Adding parallel group constraints...")
    for course_code in courses_dict.keys():
        if courses_dict[course_code]['tutorials'] > 0:
            for week in range(WEEKS):
                # Get all 4 group sessions for this tutorial
                group_sessions = [s for s in all_sessions 
                                if s['course'] == course_code and 
                                   s['type'] == 'tutorial' and 
                                   s['week'] == week]
                
                if len(group_sessions) == 4:
                    # For each day/time, either all 4 groups or none
                    for day_idx in range(len(DAYS)):
                        for time_idx in range(len(TIMESLOTS)):
                            # Get variables for each group at this time
                            group_vars_at_time = []
                            for session in group_sessions:
                                vars_for_group = [var for var_name, var in variables.items()
                                                if (var_name.startswith(session['id']) and
                                                    f"_d{day_idx}_t{time_idx}_" in var_name)]
                                if vars_for_group:
                                    # Each group can only be in one room, so sum is 0 or 1
                                    group_sum = pulp.lpSum(vars_for_group)
                                    group_vars_at_time.append(group_sum)
                            
                            # All 4 groups must have same value (all 0 or all 1)
                            if len(group_vars_at_time) == 4:
                                # If group 0 is scheduled, all others must be too
                                for i in range(1, 4):
                                    prob += group_vars_at_time[i] == group_vars_at_time[0]
    
    # CONSTRAINT 10: Each lecture/tutorial only happens once
    for session in all_sessions:
        session_vars = [var for var_name, var in variables.items() 
                       if var_name.startswith(session['id'])]
        if session_vars:
            prob += pulp.lpSum(session_vars) == 1, f"Session_{session['id']}_once"
    
    # CONSTRAINT 9: No room used by 2 classes (room conflict)
    for day_idx in range(len(DAYS)):
        for time_idx in range(len(TIMESLOTS)):
            for room in classrooms.keys():
                room_vars = [var for var_name, var in variables.items()
                           if f"_d{day_idx}_t{time_idx}_{room}" in var_name]
                if room_vars:
                    prob += pulp.lpSum(room_vars) <= 1, f"Room_{room}_d{day_idx}_t{time_idx}"
    
    # CONSTRAINT 1: Teacher can only teach ONE COURSE at the same time
    # (but can teach multiple groups of same course simultaneously)
    for day_idx in range(len(DAYS)):
        for time_idx in range(len(TIMESLOTS)):
            for teacher_name in teachers.keys():
                # Find all sessions by this teacher
                teacher_sessions_by_course = {}
                for session in all_sessions:
                    if session['teacher'] == teacher_name:
                        course = session['course']
                        if course not in teacher_sessions_by_course:
                            teacher_sessions_by_course[course] = []
                        teacher_sessions_by_course[course].append(session)
                
                # If teacher teaches only one course, no conflict possible
                if len(teacher_sessions_by_course) <= 1:
                    continue
                
                # Teacher teaches multiple courses - use Big-M method
                # At most 1 course can be active at this time
                M = 10  # Big number
                
                course_indicators = {}
                for course, sessions in teacher_sessions_by_course.items():
                    # Indicator variable: is this course scheduled?
                    ind = pulp.LpVariable(
                        f"T_{teacher_name}_{course}_d{day_idx}_t{time_idx}",
                        cat='Binary'
                    )
                    course_indicators[course] = ind
                    
                    # Get all variables for this course's sessions at this time
                    course_vars = []
                    for session in sessions:
                        for var_name, var in variables.items():
                            if (var_name.startswith(session['id']) and 
                                f"_d{day_idx}_t{time_idx}_" in var_name):
                                course_vars.append(var)
                    
                    if course_vars:
                        # If any session scheduled, indicator must be 1
                        prob += pulp.lpSum(course_vars) <= M * ind
                        # If indicator is 0, no sessions allowed
                        prob += pulp.lpSum(course_vars) >= ind
                
                # At most 1 course can have indicator = 1
                if course_indicators:
                    prob += pulp.lpSum(course_indicators.values()) <= 1, \
                            f"Teacher_{teacher_name}_onecourse_d{day_idx}_t{time_idx}"
    
    # CONSTRAINT 7: At a time slot student group has one or none lectures
    for day_idx in range(len(DAYS)):
        for time_idx in range(len(TIMESLOTS)):
            for program_name, program_data in programs.items():
                program_courses = program_data['courses']
                # Only count lectures (tutorials are in groups)
                lecture_vars = []
                for session in all_sessions:
                    if (session['program'] == program_name and 
                        session['type'] == 'lecture'):
                        for var_name, var in variables.items():
                            if (var_name.startswith(session['id']) and
                                f"_d{day_idx}_t{time_idx}_" in var_name):
                                lecture_vars.append(var)
                
                if lecture_vars:
                    prob += pulp.lpSum(lecture_vars) <= 1, f"Program_{program_name}_d{day_idx}_t{time_idx}"
    
    # CONSTRAINT 3: No scheduling at unavailable time for teachers
    # Week of Oct 27-31, 2025: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4
    date_to_day = {
        '2025-10-27': 0,  # Monday
        '2025-10-28': 1,  # Tuesday
        '2025-10-29': 2,  # Wednesday
        '2025-10-30': 3,  # Thursday
        '2025-10-31': 4   # Friday
    }
    
    for session in all_sessions:
        teacher = session['teacher']
        if teacher and teacher in teachers:
            unavailable_dates = teachers[teacher].get('unavailable', [])
            for unavail_date in unavailable_dates:
                if unavail_date in date_to_day:
                    blocked_day = date_to_day[unavail_date]
                    # Block all timeslots on this day for this teacher
                    for time_idx in range(len(TIMESLOTS)):
                        blocked_vars = [var for var_name, var in variables.items()
                                      if (var_name.startswith(session['id']) and
                                          f"_d{blocked_day}_t{time_idx}_" in var_name)]
                        if blocked_vars:
                            prob += pulp.lpSum(blocked_vars) == 0, f"Teacher_{teacher}_{session['id']}_unavail_d{blocked_day}_t{time_idx}"
    
    # CONSTRAINT 8: Flow - lectures before tutorials
    # For one week: ensure lectures happen Monday-Wednesday, tutorials Thursday-Friday
    for session in all_sessions:
        if session['type'] == 'lecture':
            # Lectures only on Mon-Wed (days 0-2)
            for day_idx in range(3, 5):  # Block Thu-Fri for lectures
                lec_vars = [var for var_name, var in variables.items()
                          if (var_name.startswith(session['id']) and
                              f"_d{day_idx}_" in var_name)]
                if lec_vars:
                    prob += pulp.lpSum(lec_vars) == 0, f"Lecture_{session['id']}_not_d{day_idx}"
        
        elif session['type'] == 'tutorial':
            # Tutorials only on Thu-Fri (days 3-4)
            for day_idx in range(0, 3):  # Block Mon-Wed for tutorials
                tut_vars = [var for var_name, var in variables.items()
                          if (var_name.startswith(session['id']) and
                              f"_d{day_idx}_" in var_name)]
                if tut_vars:
                    prob += pulp.lpSum(tut_vars) == 0, f"Tutorial_{session['id']}_not_d{day_idx}"
    
    # CONSTRAINT 2: Required hours met by end of week (already satisfied by creating sessions)
    # CONSTRAINTS 5, 6: Already built into the model (4 slots, 5 days)
    
    # Objective: Minimize something simple (or just feasibility)
    prob += 0
    
    # Solve
    print("Solving with CBC...")
    solver = pulp.PULP_CBC_CMD(msg=1, timeLimit=300)
    prob.solve(solver)
    
    print(f"Solution status: {pulp.LpStatus[prob.status]}")
    
    if prob.status != pulp.LpStatusOptimal:
        raise Exception(f"PuLP solver failed: {pulp.LpStatus[prob.status]}")
    
    # Extract solution
    schedule = extract_schedule(variables, all_sessions, courses_dict, programs, metadata)
    
    return schedule


def extract_schedule(variables, all_sessions, courses_dict, programs, metadata):
    """Extract schedule from PuLP solution"""
    schedule = {
        'metadata': metadata,
        'programs': programs,
        'schedule': {}
    }
    
    # Initialize structure
    for week in range(WEEKS):
        schedule['schedule'][f'week_{week+1}'] = {}
        for day in DAYS:
            schedule['schedule'][f'week_{week+1}'][day] = {}
            for timeslot in TIMESLOTS:
                schedule['schedule'][f'week_{week+1}'][day][timeslot] = []
    
    # Extract assigned sessions
    for var_name, var in variables.items():
        if pulp.value(var) == 1:
            # Parse variable name: sessionid_dX_tY_room
            parts = var_name.split('_')
            
            # Find session
            session_id = None
            for i, part in enumerate(parts):
                if part.startswith('d') and part[1:].isdigit():
                    session_id = '_'.join(parts[:i])
                    break
            
            if not session_id:
                continue
            
            # Find matching session
            session = next((s for s in all_sessions if s['id'] == session_id), None)
            if not session:
                continue
            
            # Extract day, time, room
            day_idx = None
            time_idx = None
            room = None
            
            for part in parts:
                if part.startswith('d') and part[1:].isdigit():
                    day_idx = int(part[1:])
                elif part.startswith('t') and part[1:].isdigit():
                    time_idx = int(part[1:])
            
            room = parts[-1]
            
            if day_idx is not None and time_idx is not None and room:
                course_data = courses_dict[session['course']]
                
                entry = {
                    'course': session['course'],
                    'course_name': course_data['name'],
                    'type': session['type'],
                    'room': room,
                    'teacher': session['teacher'],
                    'program': session['program']
                }
                
                if 'group' in session:
                    entry['group'] = session['group'] + 1
                
                week_key = f"week_{session['week']+1}"
                day_key = DAYS[day_idx]
                time_key = TIMESLOTS[time_idx]
                
                schedule['schedule'][week_key][day_key][time_key].append(entry)
    
    return schedule


if __name__ == "__main__":
    test_data = {'metadata': {'period': 'Period 2', 'year': '2024-2025', 'weeks': 7}}
    result = generate_schedule(test_data)
    print(json.dumps(result, indent=2))
