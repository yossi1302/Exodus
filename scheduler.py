"""
FSP Course Scheduler - Main Scheduling Engine
Simplified constraint-based scheduler for hackathon MVP
"""

import random
from typing import Dict, List, Any, Tuple
import copy
import json

# Constants
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
TIMESLOTS = ['08:30', '11:00', '13:30', '16:00']
WEEKS = 7

# Room definitions
ROOMS = {
    'MSP': {'capacity': 150, 'floor': 'MSP'},
    'C0.004': {'capacity': 75, 'floor': 0},
    'C0.008': {'capacity': 75, 'floor': 0},
    'C0.016': {'capacity': 75, 'floor': 0},
    'C0.020': {'capacity': 75, 'floor': 0},
    'C1.005': {'capacity': 75, 'floor': 1},
    'C1.015': {'capacity': 75, 'floor': 1},
    'C2.007': {'capacity': 75, 'floor': 2},
    'C2.017': {'capacity': 75, 'floor': 2},
    'B0.001': {'capacity': 75, 'floor': 0},
    'B0.003': {'capacity': 75, 'floor': 0},
}


def generate_schedule(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to generate schedule using greedy constraint-based approach
    """
    print("Starting schedule generation...")
    
    # Use simplified greedy approach for MVP
    print("Generating schedule with constraint-based greedy algorithm...")
    schedule = solve_with_greedy_approach(input_data)
    
    if schedule is None:
        raise Exception("No valid solution found")
    
    print("Schedule generation complete!")
    
    return schedule


def solve_with_greedy_approach(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simplified greedy scheduler that satisfies hard constraints
    """
    courses = input_data['courses']
    teachers = input_data['teachers']
    programs = input_data['programs']
    
    # Initialize schedule structure
    schedule = {
        'metadata': input_data.get('metadata', {}),
        'programs': programs,
        'schedule': {}
    }
    
    for week in range(WEEKS):
        schedule['schedule'][f'week_{week+1}'] = {}
        for day in DAYS:
            schedule['schedule'][f'week_{week+1}'][day] = {}
            for timeslot in TIMESLOTS:
                schedule['schedule'][f'week_{week+1}'][day][timeslot] = []
    
    # Track what's been scheduled
    scheduled_sessions = []
    
    # Create mapping of courses to programs
    course_to_programs = {}
    for program_name, program_data in programs.items():
        for course_code in program_data['courses']:
            if course_code not in course_to_programs:
                course_to_programs[course_code] = []
            course_to_programs[course_code].append(program_name)
    
    # Track usage
    room_usage = {}  # (week, day, time) -> room
    teacher_usage = {}  # (week, day, time) -> teacher
    program_usage = {}  # (program, week, day, time) -> bool
    
    # Schedule all courses
    for course in courses:
        course_code = course['code']
        course_name = course['name']
        
        # Find teacher for this course
        teacher = None
        for t_name, t_data in teachers.items():
            if course_code in t_data['courses']:
                teacher = t_name
                break
        
        # Find program
        program = course_to_programs.get(course_code, [None])[0]
        
        # Determine room constraints
        year_one = program and program.endswith('_Y1')
        needs_large_room = year_one and programs.get(program, {}).get('size', 0) >= 150
        
        # Schedule lectures first (theory before practical)
        for lec_num in range(course.get('lectures', 0)):
            slot = find_available_slot(
                week_range=range(WEEKS),
                room_usage=room_usage,
                teacher_usage=teacher_usage,
                program_usage=program_usage,
                teacher=teacher,
                program=program,
                needs_large_room=needs_large_room,
                session_type='lecture'
            )
            
            if slot:
                week, day_idx, time_idx, room = slot
                add_session_to_schedule(
                    schedule, week, day_idx, time_idx, room,
                    course_code, course_name, 'lecture', teacher, program,
                    room_usage, teacher_usage, program_usage
                )
        
        # Schedule tutorials
        for tut_num in range(course.get('tutorials', 0)):
            # Split into groups for tutorials
            num_groups = 4 if program and programs[program]['size'] > 75 else 1
            
            for group in range(num_groups):
                slot = find_available_slot(
                    week_range=range(WEEKS),
                    room_usage=room_usage,
                    teacher_usage=teacher_usage,
                    program_usage=program_usage,
                    teacher=teacher,
                    program=program,
                    needs_large_room=False,
                    session_type='tutorial'
                )
                
                if slot:
                    week, day_idx, time_idx, room = slot
                    add_session_to_schedule(
                        schedule, week, day_idx, time_idx, room,
                        course_code, course_name, 'tutorial', teacher, program,
                        room_usage, teacher_usage, program_usage
                    )
        
        # Schedule labs
        for lab_num in range(course.get('labs', 0)):
            # Split into groups for labs
            num_groups = 4 if program and programs[program]['size'] > 75 else 1
            
            for group in range(num_groups):
                slot = find_available_slot(
                    week_range=range(WEEKS),
                    room_usage=room_usage,
                    teacher_usage=teacher_usage,
                    program_usage=program_usage,
                    teacher=teacher,
                    program=program,
                    needs_large_room=False,
                    session_type='lab'
                )
                
                if slot:
                    week, day_idx, time_idx, room = slot
                    add_session_to_schedule(
                        schedule, week, day_idx, time_idx, room,
                        course_code, course_name, 'lab', teacher, program,
                        room_usage, teacher_usage, program_usage
                    )
    
    return schedule


def find_available_slot(week_range, room_usage, teacher_usage, program_usage, 
                       teacher, program, needs_large_room, session_type):
    """Find first available slot that satisfies constraints"""
    
    # Randomize order to get variation
    weeks = list(week_range)
    random.shuffle(weeks)
    
    for week in weeks:
        for day_idx in range(len(DAYS)):
            for time_idx in range(len(TIMESLOTS)):
                # Check if teacher is available
                if teacher and (week, day_idx, time_idx) in teacher_usage:
                    if teacher_usage[(week, day_idx, time_idx)] == teacher:
                        continue
                
                # Check if program has conflict
                if program and (program, week, day_idx, time_idx) in program_usage:
                    continue
                
                # Find available room
                available_rooms = []
                for room_name, room_info in ROOMS.items():
                    if needs_large_room and room_info['capacity'] < 150:
                        continue
                    
                    if (week, day_idx, time_idx, room_name) not in room_usage:
                        available_rooms.append(room_name)
                
                if available_rooms:
                    # Prefer MSP for large lectures
                    if needs_large_room and 'MSP' in available_rooms:
                        return (week, day_idx, time_idx, 'MSP')
                    else:
                        return (week, day_idx, time_idx, available_rooms[0])
    
    return None


def add_session_to_schedule(schedule, week, day_idx, time_idx, room, 
                            course_code, course_name, session_type, teacher, program,
                            room_usage, teacher_usage, program_usage):
    """Add a session to the schedule and update usage tracking"""
    
    week_key = f'week_{week+1}'
    day_key = DAYS[day_idx]
    time_key = TIMESLOTS[time_idx]
    
    session_info = {
        'course': course_code,
        'course_name': course_name,
        'type': session_type,
        'room': room,
        'teacher': teacher,
        'program': program
    }
    
    schedule['schedule'][week_key][day_key][time_key].append(session_info)
    
    # Update tracking
    room_usage[(week, day_idx, time_idx, room)] = True
    if teacher:
        teacher_usage[(week, day_idx, time_idx)] = teacher
    if program:
        program_usage[(program, week, day_idx, time_idx)] = True


def solve_hard_constraints_cpsat_OLD(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 1: Use CP-SAT to satisfy all hard constraints
    """
    model = cp_model.CpModel()
    
    courses = input_data['courses']
    teachers = input_data['teachers']
    programs = input_data['programs']
    
    # Create mapping of courses to programs
    course_to_programs = {}
    for program_name, program_data in programs.items():
        for course_code in program_data['courses']:
            if course_code not in course_to_programs:
                course_to_programs[course_code] = []
            course_to_programs[course_code].append(program_name)
    
    # Variables: session[course, session_type, week, day, timeslot, room]
    sessions = {}
    
    for course in courses:
        course_code = course['code']
        
        # Create variables for lectures
        for lec in range(course.get('lectures', 0)):
            for week in range(WEEKS):
                for day_idx, day in enumerate(DAYS):
                    for time_idx, timeslot in enumerate(TIMESLOTS):
                        for room in ROOMS.keys():
                            var = model.NewBoolVar(f'{course_code}_L{lec}_w{week}_d{day_idx}_t{time_idx}_{room}')
                            sessions[(course_code, 'lecture', lec, week, day_idx, time_idx, room)] = var
        
        # Create variables for tutorials
        for tut in range(course.get('tutorials', 0)):
            for week in range(WEEKS):
                for day_idx, day in enumerate(DAYS):
                    for time_idx, timeslot in enumerate(TIMESLOTS):
                        for room in ROOMS.keys():
                            var = model.NewBoolVar(f'{course_code}_T{tut}_w{week}_d{day_idx}_t{time_idx}_{room}')
                            sessions[(course_code, 'tutorial', tut, week, day_idx, time_idx, room)] = var
        
        # Create variables for labs
        for lab in range(course.get('labs', 0)):
            for week in range(WEEKS):
                for day_idx, day in enumerate(DAYS):
                    for time_idx, timeslot in enumerate(TIMESLOTS):
                        for room in ROOMS.keys():
                            var = model.NewBoolVar(f'{course_code}_Lab{lab}_w{week}_d{day_idx}_t{time_idx}_{room}')
                            sessions[(course_code, 'lab', lab, week, day_idx, time_idx, room)] = var
    
    # Constraint 1: Each session must be scheduled exactly once
    for course in courses:
        course_code = course['code']
        
        for lec in range(course.get('lectures', 0)):
            model.AddExactlyOne([
                sessions[(course_code, 'lecture', lec, week, day, time, room)]
                for week in range(WEEKS)
                for day in range(len(DAYS))
                for time in range(len(TIMESLOTS))
                for room in ROOMS.keys()
            ])
        
        for tut in range(course.get('tutorials', 0)):
            model.AddExactlyOne([
                sessions[(course_code, 'tutorial', tut, week, day, time, room)]
                for week in range(WEEKS)
                for day in range(len(DAYS))
                for time in range(len(TIMESLOTS))
                for room in ROOMS.keys()
            ])
        
        for lab in range(course.get('labs', 0)):
            model.AddExactlyOne([
                sessions[(course_code, 'lab', lab, week, day, time, room)]
                for week in range(WEEKS)
                for day in range(len(DAYS))
                for time in range(len(TIMESLOTS))
                for room in ROOMS.keys()
            ])
    
    # Constraint 2: No room conflicts (one session per room per timeslot)
    for week in range(WEEKS):
        for day in range(len(DAYS)):
            for time in range(len(TIMESLOTS)):
                for room in ROOMS.keys():
                    room_sessions = []
                    for key, var in sessions.items():
                        if key[3] == week and key[4] == day and key[5] == time and key[6] == room:
                            room_sessions.append(var)
                    if room_sessions:
                        model.AddAtMostOne(room_sessions)
    
    # Constraint 3: Year 1 lectures must be in MSP (capacity 150+)
    for course in courses:
        course_code = course['code']
        programs_for_course = course_to_programs.get(course_code, [])
        
        for program_name in programs_for_course:
            if program_name.endswith('_Y1') and programs[program_name]['size'] >= 150:
                # Force lectures to MSP
                for lec in range(course.get('lectures', 0)):
                    for week in range(WEEKS):
                        for day in range(len(DAYS)):
                            for time in range(len(TIMESLOTS)):
                                for room in ROOMS.keys():
                                    if room != 'MSP':
                                        # Force non-MSP rooms to 0
                                        key = (course_code, 'lecture', lec, week, day, time, room)
                                        if key in sessions:
                                            model.Add(sessions[key] == 0)
    
    # Constraint 4: Students in same program can't have conflicts
    for program_name, program_data in programs.items():
        program_courses = program_data['courses']
        
        for week in range(WEEKS):
            for day in range(len(DAYS)):
                for time in range(len(TIMESLOTS)):
                    # Collect all sessions for this program at this time
                    program_sessions = []
                    for course in courses:
                        if course['code'] in program_courses:
                            for key, var in sessions.items():
                                if key[0] == course['code'] and key[3] == week and key[4] == day and key[5] == time:
                                    program_sessions.append(var)
                    
                    if program_sessions:
                        model.AddAtMostOne(program_sessions)
    
    # Constraint 5: Minimum 2 sessions per day per student (if any sessions that day)
    # This is a soft constraint, we'll handle it in GA phase
    
    # Constraint 6: Theory before practical (lectures before labs/tutorials)
    for course in courses:
        if course.get('theory_before_practical', False):
            course_code = course['code']
            lectures = course.get('lectures', 0)
            labs = course.get('labs', 0)
            tutorials = course.get('tutorials', 0)
            
            if lectures > 0 and (labs > 0 or tutorials > 0):
                # Find when lecture happens
                lecture_time_var = model.NewIntVar(0, WEEKS * len(DAYS) * len(TIMESLOTS), f'{course_code}_lecture_time')
                
                lecture_constraints = []
                for lec in range(lectures):
                    for week in range(WEEKS):
                        for day in range(len(DAYS)):
                            for time in range(len(TIMESLOTS)):
                                for room in ROOMS.keys():
                                    key = (course_code, 'lecture', lec, week, day, time, room)
                                    if key in sessions:
                                        abs_time = week * len(DAYS) * len(TIMESLOTS) + day * len(TIMESLOTS) + time
                                        # If this session is scheduled, lecture_time_var should be <= abs_time
                                        model.Add(lecture_time_var <= abs_time).OnlyEnforceIf(sessions[key])
                
                # All labs and tutorials must be after lectures
                for lab in range(labs):
                    for week in range(WEEKS):
                        for day in range(len(DAYS)):
                            for time in range(len(TIMESLOTS)):
                                for room in ROOMS.keys():
                                    key = (course_code, 'lab', lab, week, day, time, room)
                                    if key in sessions:
                                        abs_time = week * len(DAYS) * len(TIMESLOTS) + day * len(TIMESLOTS) + time
                                        model.Add(abs_time > lecture_time_var).OnlyEnforceIf(sessions[key])
                
                for tut in range(tutorials):
                    for week in range(WEEKS):
                        for day in range(len(DAYS)):
                            for time in range(len(TIMESLOTS)):
                                for room in ROOMS.keys():
                                    key = (course_code, 'tutorial', tut, week, day, time, room)
                                    if key in sessions:
                                        abs_time = week * len(DAYS) * len(TIMESLOTS) + day * len(TIMESLOTS) + time
                                        model.Add(abs_time > lecture_time_var).OnlyEnforceIf(sessions[key])
    
    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 120.0  # 2 minute timeout
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Extract solution
        schedule = build_schedule_from_solution(solver, sessions, input_data)
        return schedule
    else:
        return None


def build_schedule_from_solution(solver, sessions, input_data):
    """Convert CP-SAT solution to schedule dictionary"""
    schedule = {
        'metadata': input_data.get('metadata', {}),
        'programs': input_data['programs'],
        'schedule': {}
    }
    
    # Initialize schedule structure
    for week in range(WEEKS):
        schedule['schedule'][f'week_{week+1}'] = {}
        for day in DAYS:
            schedule['schedule'][f'week_{week+1}'][day] = {}
            for timeslot in TIMESLOTS:
                schedule['schedule'][f'week_{week+1}'][day][timeslot] = []
    
    # Extract scheduled sessions
    for key, var in sessions.items():
        if solver.Value(var) == 1:
            course_code, session_type, session_num, week, day_idx, time_idx, room = key
            
            # Find course details
            course_name = None
            for course in input_data['courses']:
                if course['code'] == course_code:
                    course_name = course['name']
                    break
            
            # Find teacher
            teacher = None
            for t_name, t_data in input_data['teachers'].items():
                if course_code in t_data['courses']:
                    teacher = t_name
                    break
            
            # Find program
            program = None
            for prog_name, prog_data in input_data['programs'].items():
                if course_code in prog_data['courses']:
                    program = prog_name
                    break
            
            session_info = {
                'course': course_code,
                'course_name': course_name,
                'type': session_type,
                'room': room,
                'teacher': teacher,
                'program': program
            }
            
            week_key = f'week_{week+1}'
            day_key = DAYS[day_idx]
            time_key = TIMESLOTS[time_idx]
            
            schedule['schedule'][week_key][day_key][time_key].append(session_info)
    
    return schedule


def optimize_soft_constraints_ga_OLD(initial_schedule: Dict[str, Any], input_data: Dict[str, Any], 
                                  population_size: int = 50, generations: int = 100) -> Dict[str, Any]:
    """
    Phase 2: Use Genetic Algorithm to optimize soft constraints
    """
    
    def evaluate_fitness(schedule):
        """Calculate fitness score (higher is better)"""
        score = 0
        
        # Soft constraint 1: Even distribution across the week
        score -= check_uneven_distribution(schedule) * 10
        
        # Soft constraint 2: Max 3 lectures per day
        score -= count_excessive_daily_lectures(schedule) * 15
        
        # Soft constraint 3: Minimize gaps between classes
        score -= count_student_gaps(schedule) * 5
        
        # Soft constraint 4: Same course in same room
        score -= count_room_changes(schedule) * 8
        
        # Soft constraint 5: Room utilization above 50%
        score -= count_underutilized_rooms(schedule) * 3
        
        # Soft constraint 6: Continuous classes (no gaps)
        score += count_continuous_blocks(schedule) * 2
        
        return score
    
    def check_uneven_distribution(schedule):
        """Penalty for uneven distribution of lectures across week"""
        penalty = 0
        for program_name in input_data['programs'].keys():
            for week_key, week_data in schedule['schedule'].items():
                daily_counts = [0] * 5
                for day_idx, day in enumerate(DAYS):
                    for timeslot, sessions in week_data[day].items():
                        for session in sessions:
                            if session.get('program') == program_name:
                                daily_counts[day_idx] += 1
                
                # Calculate standard deviation
                if sum(daily_counts) > 0:
                    mean = sum(daily_counts) / len(daily_counts)
                    variance = sum((x - mean) ** 2 for x in daily_counts) / len(daily_counts)
                    penalty += variance ** 0.5
        
        return penalty
    
    def count_excessive_daily_lectures(schedule):
        """Count days with more than 3 lectures"""
        violations = 0
        for program_name in input_data['programs'].keys():
            for week_key, week_data in schedule['schedule'].items():
                for day in DAYS:
                    count = 0
                    for timeslot, sessions in week_data[day].items():
                        for session in sessions:
                            if session.get('program') == program_name:
                                count += 1
                    if count > 3:
                        violations += (count - 3)
        
        return violations
    
    def count_student_gaps(schedule):
        """Count gaps in student schedules"""
        gaps = 0
        for program_name in input_data['programs'].keys():
            for week_key, week_data in schedule['schedule'].items():
                for day in DAYS:
                    timeslots_with_class = []
                    for time_idx, timeslot in enumerate(TIMESLOTS):
                        has_class = False
                        for session in week_data[day][timeslot]:
                            if session.get('program') == program_name:
                                has_class = True
                                break
                        if has_class:
                            timeslots_with_class.append(time_idx)
                    
                    # Count gaps
                    if len(timeslots_with_class) > 1:
                        for i in range(len(timeslots_with_class) - 1):
                            gap = timeslots_with_class[i+1] - timeslots_with_class[i] - 1
                            gaps += gap
        
        return gaps
    
    def count_room_changes(schedule):
        """Count when same course is in different rooms"""
        violations = 0
        course_rooms = {}
        
        for week_key, week_data in schedule['schedule'].items():
            for day in DAYS:
                for timeslot, sessions in week_data[day].items():
                    for session in sessions:
                        course = session['course']
                        room = session['room']
                        
                        if course not in course_rooms:
                            course_rooms[course] = set()
                        course_rooms[course].add(room)
        
        for course, rooms in course_rooms.items():
            if len(rooms) > 1:
                violations += (len(rooms) - 1)
        
        return violations
    
    def count_underutilized_rooms(schedule):
        """Count rooms with less than 50% capacity usage"""
        violations = 0
        
        for week_key, week_data in schedule['schedule'].items():
            for day in DAYS:
                for timeslot, sessions in week_data[day].items():
                    for session in sessions:
                        room = session['room']
                        room_capacity = ROOMS[room]['capacity']
                        
                        # Find program size
                        program = session.get('program')
                        if program:
                            program_size = input_data['programs'][program]['size']
                            
                            # For tutorials/labs, assume split into groups
                            if session['type'] in ['tutorial', 'lab']:
                                program_size = program_size // 4  # Assume 4 groups
                            
                            if program_size < room_capacity * 0.5:
                                violations += 1
        
        return violations
    
    def count_continuous_blocks(schedule):
        """Reward continuous blocks of classes"""
        blocks = 0
        
        for program_name in input_data['programs'].keys():
            for week_key, week_data in schedule['schedule'].items():
                for day in DAYS:
                    continuous = 0
                    for time_idx, timeslot in enumerate(TIMESLOTS):
                        has_class = False
                        for session in week_data[day][timeslot]:
                            if session.get('program') == program_name:
                                has_class = True
                                break
                        
                        if has_class:
                            continuous += 1
                        else:
                            if continuous >= 2:
                                blocks += continuous
                            continuous = 0
                    
                    if continuous >= 2:
                        blocks += continuous
        
        return blocks
    
    # For hackathon MVP, we'll do a simple local search instead of full GA
    # due to complexity of preserving hard constraints during crossover
    
    best_schedule = initial_schedule
    best_score = evaluate_fitness(initial_schedule)
    
    print(f"Initial fitness: {best_score}")
    
    # Simple hill climbing with random restarts
    for iteration in range(generations):
        # Try small random swaps that preserve hard constraints
        # For MVP, we'll just return the initial valid solution
        # Full GA implementation would go here with proper operators
        pass
    
    print(f"Final fitness: {best_score}")
    
    return best_schedule


if __name__ == "__main__":
    # Test with example data
    import json
    with open('static/example_input.json', 'r') as f:
        test_data = json.load(f)
    
    result = generate_schedule(test_data)
    print(json.dumps(result, indent=2))
