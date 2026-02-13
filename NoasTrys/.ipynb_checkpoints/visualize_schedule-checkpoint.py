"""
Visual Schedule Display Tool
Creates beautiful visual representations of the course schedule
WITH INTERACTIVE YEAR FILTERING!
"""

import pandas as pd
from IPython.display import HTML, display

def create_schedule_dataframe(x, params):
    """
    Extract schedule from PuLP variables into a DataFrame
    
    Parameters:
    -----------
    x : dict
        PuLP decision variables
    params : dict
        Problem parameters
        
    Returns:
    --------
    pd.DataFrame
        Schedule with all details
    """
    DAY_NAMES = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday'}
    TIME_NAMES = {1: '08:30-10:30', 2: '11:00-13:00', 3: '13:30-15:30', 4: '16:00-18:00'}
    
    schedule_data = []
    
    for (c, i, r, d, t), var in x.items():
        if var.varValue == 1:
            schedule_data.append({
                'Day': DAY_NAMES[d],
                'Day_Num': d,
                'Time': TIME_NAMES[t],
                'Time_Num': t,
                'Course': c,
                'Session': i,
                'Type': params['Timeline'][c][i],
                'Room': r,
                'Lecturer': params['Lecturer'][c],
                'Students': params['students_per_course'][c],
                'Room_Capacity': params['Cap'][r]
            })
    
    df = pd.DataFrame(schedule_data)
    
    # Sort by day and time
    df = df.sort_values(['Day_Num', 'Time_Num']).reset_index(drop=True)
    
    return df


def print_schedule_by_day(df):
    """
    Print schedule organized by day in a clean format
    """
    print("\n" + "="*100)
    print("WEEKLY SCHEDULE")
    print("="*100)
    
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        day_schedule = df[df['Day'] == day]
        
        if len(day_schedule) > 0:
            print(f"\n{'='*100}")
            print(f"{day.upper()}")
            print(f"{'='*100}")
            
            for time in ['08:30-10:30', '11:00-13:00', '13:30-15:30', '16:00-18:00']:
                time_slots = day_schedule[day_schedule['Time'] == time]
                
                if len(time_slots) > 0:
                    print(f"\n{time}:")
                    for _, session in time_slots.iterrows():
                        session_type = 'Lecture' if session['Type'] == 'C' else 'Tutorial'
                        print(f"  • {session['Course']} - Session {session['Session']} ({session_type})")
                        print(f"    Room: {session['Room']} (capacity {session['Room_Capacity']})")
                        print(f"    Lecturer: {session['Lecturer']}")
                        print(f"    Students: {session['Students']}")


def create_grid_view(df):
    """
    Create a grid view showing all rooms across all time slots
    """
    print("\n" + "="*150)
    print("GRID VIEW - ALL ROOMS")
    print("="*150)
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = ['08:30-10:30', '11:00-13:00', '13:30-15:30', '16:00-18:00']
    
    for day in days:
        print(f"\n{'='*150}")
        print(f"{day.upper()}")
        print(f"{'='*150}")
        
        day_schedule = df[df['Day'] == day]
        
        for time in times:
            time_slots = day_schedule[day_schedule['Time'] == time]
            
            print(f"\n{time:15}", end="")
            
            if len(time_slots) == 0:
                print("  [No classes scheduled]")
            else:
                print()
                for _, session in time_slots.iterrows():
                    session_type = 'Lec' if session['Type'] == 'C' else 'Tut'
                    print(f"  {session['Room']:7} → {session['Course']} S{session['Session']} ({session_type}) - {session['Lecturer']}")


def create_html_calendar(df, params):
    """
    Create an interactive HTML calendar view with year filtering
    """
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = ['08:30-10:30', '11:00-13:00', '13:30-15:30', '16:00-18:00']
    
    # Color scheme for courses
    courses = df['Course'].unique()
    colors = [
        '#FFB6C1', '#87CEEB', '#98FB98', '#DDA0DD', '#F0E68C',
        '#FFB347', '#B19CD9', '#AEC6CF', '#CFCFC4', '#FDFD96',
        '#FF6961', '#77DD77'
    ]
    course_colors = {course: colors[i % len(colors)] for i, course in enumerate(courses)}
    
    # Map courses to programs
    course_to_programs = {}
    for course in courses:
        course_programs = []
        for program, program_courses in params['Courses'].items():
            if course in program_courses:
                course_programs.append(program)
        course_to_programs[course] = course_programs
    
    html = """
    <style>
        .schedule-container {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        .filter-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 2px solid #dee2e6;
        }
        .filter-title {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .filter-options {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .filter-option {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 15px;
            background-color: white;
            border-radius: 5px;
            border: 2px solid #dee2e6;
            cursor: pointer;
            transition: all 0.3s;
        }
        .filter-option:hover {
            border-color: #2c3e50;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .filter-option input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        .filter-option label {
            cursor: pointer;
            font-weight: 500;
            color: #2c3e50;
            user-select: none;
        }
        .schedule-table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }
        .schedule-table th {
            background-color: #2c3e50;
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: bold;
        }
        .schedule-table td {
            border: 1px solid #ddd;
            padding: 8px;
            vertical-align: top;
            min-height: 100px;
        }
        .time-cell {
            background-color: #ecf0f1;
            font-weight: bold;
            text-align: center;
            width: 100px;
        }
        .session-card {
            margin: 5px;
            padding: 8px;
            border-radius: 5px;
            border-left: 4px solid #2c3e50;
            font-size: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: opacity 0.3s;
        }
        .session-card.hidden {
            display: none;
        }
        .course-code {
            font-weight: bold;
            font-size: 13px;
        }
        .session-info {
            font-size: 11px;
            color: #555;
            margin-top: 3px;
        }
        .lecturer-info {
            font-size: 11px;
            color: #666;
            font-style: italic;
        }
        h2 {
            color: #2c3e50;
        }
    </style>
    
    <div class="schedule-container">
        <h2>📅 Weekly Course Schedule</h2>
        
        <!-- Filter Section -->
        <div class="filter-container">
            <div class="filter-title">🎓 Filter by Program/Year:</div>
            <div class="filter-options">
                <div class="filter-option">
                    <input type="checkbox" id="filter_CS_Y1" value="CS_Y1" checked onchange="filterSchedule()">
                    <label for="filter_CS_Y1">CS Year 1</label>
                </div>
                <div class="filter-option">
                    <input type="checkbox" id="filter_CS_Y2" value="CS_Y2" checked onchange="filterSchedule()">
                    <label for="filter_CS_Y2">CS Year 2</label>
                </div>
                <div class="filter-option">
                    <input type="checkbox" id="filter_DS_Y1" value="DS_Y1" checked onchange="filterSchedule()">
                    <label for="filter_DS_Y1">DS Year 1</label>
                </div>
                <div class="filter-option">
                    <input type="checkbox" id="filter_DS_Y2" value="DS_Y2" checked onchange="filterSchedule()">
                    <label for="filter_DS_Y2">DS Year 2</label>
                </div>
            </div>
        </div>
        
        <table class="schedule-table">
            <thead>
                <tr>
                    <th>Time</th>
    """
    
    # Add day headers
    for day in days:
        html += f"<th>{day}</th>\n"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    # Add time slots
    for time in times:
        html += f"""
                <tr>
                    <td class="time-cell">{time}</td>
        """
        
        for day in days:
            # Get all sessions for this day/time
            sessions = df[(df['Day'] == day) & (df['Time'] == time)]
            
            html += '<td>'
            
            for _, session in sessions.iterrows():
                session_type = 'Lecture' if session['Type'] == 'C' else 'Tutorial'
                color = course_colors[session['Course']]
                
                # Get programs for this course
                programs = course_to_programs[session['Course']]
                programs_str = ' '.join(programs)
                
                html += f"""
                    <div class="session-card" data-programs="{programs_str}" style="background-color: {color};">
                        <div class="course-code">{session['Course']} - Session {session['Session']}</div>
                        <div class="session-info">
                            {session_type} | Room {session['Room']}<br>
                            {session['Students']} students
                        </div>
                        <div class="lecturer-info">{session['Lecturer']}</div>
                    </div>
                """
            
            html += '</td>\n'
        
        html += '    </tr>\n'
    
    html += """
            </tbody>
        </table>
    </div>
    
    <script>
        function filterSchedule() {
            // Get checked programs
            const checkedPrograms = new Set();
            const checkboxes = document.querySelectorAll('.filter-option input[type="checkbox"]');
            
            checkboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    checkedPrograms.add(checkbox.value);
                }
            });
            
            // Show/hide session cards based on filter
            const sessionCards = document.querySelectorAll('.session-card');
            
            sessionCards.forEach(card => {
                const cardPrograms = card.getAttribute('data-programs').split(' ');
                
                // Show card if ANY of its programs are checked
                const shouldShow = cardPrograms.some(program => checkedPrograms.has(program));
                
                if (shouldShow) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        }
        
        // Initialize on page load
        filterSchedule();
    </script>
    """
    
    # Add legend
    html += """
    <div class="schedule-container">
        <h3>Course Legend:</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
    """
    
    for course in sorted(courses):
        lecturer = df[df['Course'] == course]['Lecturer'].iloc[0]
        students = df[df['Course'] == course]['Students'].iloc[0]
        color = course_colors[course]
        programs = ', '.join(course_to_programs[course])
        
        html += f"""
            <div style="padding: 8px 15px; background-color: {color}; border-radius: 5px; border-left: 4px solid #2c3e50;">
                <strong>{course}</strong><br>
                <small>{lecturer} | {students} students | {programs}</small>
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html


def create_lecturer_schedule(df):
    """
    Create a schedule view organized by lecturer
    """
    print("\n" + "="*100)
    print("SCHEDULE BY LECTURER")
    print("="*100)
    
    lecturers = sorted(df['Lecturer'].unique())
    
    for lecturer in lecturers:
        lecturer_sessions = df[df['Lecturer'] == lecturer].sort_values(['Day_Num', 'Time_Num'])
        
        print(f"\n{lecturer}:")
        print("-" * 80)
        
        for _, session in lecturer_sessions.iterrows():
            session_type = 'Lecture' if session['Type'] == 'C' else 'Tutorial'
            print(f"  {session['Day']:10} {session['Time']:15} | {session['Course']:10} Session {session['Session']} ({session_type}) | Room {session['Room']}")


def create_room_schedule(df):
    """
    Create a schedule view organized by room
    """
    print("\n" + "="*100)
    print("SCHEDULE BY ROOM")
    print("="*100)
    
    rooms = sorted(df['Room'].unique())
    
    for room in rooms:
        room_sessions = df[df['Room'] == room].sort_values(['Day_Num', 'Time_Num'])
        capacity = room_sessions['Room_Capacity'].iloc[0]
        
        print(f"\n{room} (Capacity: {capacity}):")
        print("-" * 80)
        
        if len(room_sessions) == 0:
            print("  [Not used]")
        else:
            for _, session in room_sessions.iterrows():
                session_type = 'Lecture' if session['Type'] == 'C' else 'Tutorial'
                utilization = f"{100 * session['Students'] / capacity:.0f}%"
                print(f"  {session['Day']:10} {session['Time']:15} | {session['Course']:10} Session {session['Session']} - {session['Students']} students ({utilization} full)")


def display_all_views(x, params):
    """
    Display all schedule views
    
    Usage in notebook:
    ------------------
    from visualize_schedule import display_all_views
    display_all_views(x, clean_params)
    """
    # Create dataframe
    df = create_schedule_dataframe(x, params)
    
    # Print summary
    print("\n" + "="*100)
    print("SCHEDULE SUMMARY")
    print("="*100)
    print(f"Total sessions scheduled: {len(df)}")
    print(f"Courses: {df['Course'].nunique()}")
    print(f"Rooms used: {df['Room'].nunique()}")
    print(f"Lecturers: {df['Lecturer'].nunique()}")
    
    # Display different views
    print_schedule_by_day(df)
    create_grid_view(df)
    create_lecturer_schedule(df)
    create_room_schedule(df)
    
    # Display HTML calendar
    print("\n" + "="*100)
    print("Displaying interactive HTML calendar view below...")
    print("="*100)
    
    html_calendar = create_html_calendar(df, params)
    display(HTML(html_calendar))
    
    return df


if __name__ == "__main__":
    print("""
    Visual Schedule Display Tool
    ============================
    
    Usage in Jupyter notebook:
    
    from visualize_schedule import display_all_views
    
    # After solving your model:
    df = display_all_views(x, params)
    
    # Or use individual functions:
    from visualize_schedule import create_schedule_dataframe, create_html_calendar
    df = create_schedule_dataframe(x, params)
    html = create_html_calendar(df, params)
    display(HTML(html))
    """)