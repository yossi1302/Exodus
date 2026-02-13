"""
Filter out courses with 0 students before running the model

Zero-student courses can cause infeasibility if they're listed
in program requirements but have no actual enrollment.
"""

def filter_zero_student_courses(params):
    """
    Remove courses with 0 students from the problem
    """
    print("\n" + "="*80)
    print("FILTERING ZERO-STUDENT COURSES")
    print("="*80)
    
    # Find courses with 0 students
    zero_courses = [c for c in params['C'] if params['students_per_course'][c] == 0]
    
    if not zero_courses:
        print("\n✅ No zero-student courses found. No filtering needed.")
        return params
    
    print(f"\n⚠️  Found {len(zero_courses)} courses with 0 students:")
    for c in zero_courses:
        print(f"  - {c}")
    
    # Create filtered parameters
    filtered_params = params.copy()
    
    # Remove from course list
    filtered_params['C'] = [c for c in params['C'] if c not in zero_courses]
    
    # Remove from program requirements
    filtered_courses_per_program = {}
    for p in params['P']:
        filtered_courses_per_program[p] = [
            c for c in params['Courses'][p] 
            if c not in zero_courses
        ]
    filtered_params['Courses'] = filtered_courses_per_program
    
    # Remove course-specific data for zero-student courses
    for key in ['I', 'Timeline', 'Lecturer', 'students_per_course']:
        if key in filtered_params:
            filtered_params[key] = {
                c: v for c, v in filtered_params[key].items() 
                if c not in zero_courses
            }
    
    # Keep non-course parameters as-is (U is lecturer-based, not course-based)
    # These should already be in filtered_params from the .copy(), but make sure:
    for key in ['U', 'Cap', 'R', 'L', 'D', 'T', 'P', 'n']:
        if key in params and key not in filtered_params:
            filtered_params[key] = params[key]
    
    print(f"\n✅ Filtered parameters created")
    print(f"   Original courses: {len(params['C'])}")
    print(f"   Filtered courses: {len(filtered_params['C'])}")
    print(f"   Courses remaining: {filtered_params['C']}")
    
    # Verify programs still have courses
    print("\nProgram course counts after filtering:")
    for p in filtered_params['P']:
        course_count = len(filtered_params['Courses'][p])
        print(f"  {p}: {course_count} courses")
        if course_count == 0:
            print(f"    ⚠️  WARNING: {p} has no courses after filtering!")
    
    # Verify U parameter is present
    print("\nLecturer unavailability data:")
    if 'U' in filtered_params and filtered_params['U']:
        for l, days in filtered_params['U'].items():
            if days:
                print(f"  {l}: {days}")
    else:
        print("  ⚠️  WARNING: No unavailability data found!")
    
    print("\n" + "="*80)
    
    return filtered_params


def create_clean_params(params):
    """
    Create a cleaned version of params ready for optimization
    """
    # Filter zero-student courses
    clean_params = filter_zero_student_courses(params)
    
    # Calculate total sessions
    total_sessions = sum(len(clean_params['I'][c]) for c in clean_params['C'])
    print(f"\nTotal sessions to schedule: {total_sessions}")
    
    return clean_params


if __name__ == "__main__":
    print("Run this from notebook:")
    print("  %run load_parameters.py")
    print("  %run clean_data.py")
    print("  clean_params = create_clean_params(params)")
    print("  # Then use clean_params instead of params in your model")