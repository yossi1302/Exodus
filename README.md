# FSP Course Scheduler - MVP

Automated course scheduling system for Faculty of Science and Engineering, Maastricht University.

## Features

- **JSON Input**: Upload course requirements, teacher availability, and program details
- **Smart Scheduling**: Constraint-based greedy algorithm ensures all hard constraints are met
- **Interactive View**: Web-based schedule viewer with program filtering
- **Export Options**: Download schedules as PDF or Excel

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python3 app.py
```

The application will be available at `http://localhost:5000`

### 3. Upload Schedule Requirements

1. Go to "Create Schedule" 
2. Download the example JSON template or create your own
3. Upload your JSON file
4. Wait for the schedule to be generated (may take 1-2 minutes)
5. View and export your schedule

## JSON Input Format

```json
{
  "metadata": {
    "period": "Period 2",
    "year": "2024-2025",
    "weeks": 7
  },
  "courses": [
    {
      "code": "BCS1220",
      "name": "Objects in Programming (OIP)",
      "lectures": 1,
      "tutorials": 1,
      "labs": 2,
      "hours_per_session": 2,
      "theory_before_practical": true
    }
  ],
  "teachers": {
    "Teacher Name": {
      "courses": ["BCS1220"],
      "unavailable": ["Monday-08:30", "Wednesday-16:00"]
    }
  },
  "programs": {
    "CS_Y1": {
      "size": 300,
      "courses": ["BCS1220", "BCS1440", "BCS1530"]
    },
    "DS_Y1": {
      "size": 300,
      "courses": ["KEN1220", "KEN1440", "KEN1530"]
    }
  }
}
```

## Hard Constraints (Always Satisfied)

1. ✓ Teacher can only teach one course at a time
2. ✓ Students in a program can only take one course at a time  
3. ✓ All required sessions are scheduled
4. ✓ No scheduling at unavailable teacher times
5. ✓ Room capacity constraints (Year 1 lectures in MSP)
6. ✓ Theory lectures before practical sessions
7. ✓ 4 time slots per day × 5 weekdays

## Soft Constraints (Optimized)

- Even distribution across the week
- Maximum 3 lectures per day per student
- Minimize gaps between classes
- Same course in same room when possible
- Continuous class blocks preferred

## Time Slots

- **Morning 1**: 08:30 – 10:30
- **Morning 2**: 11:00 – 13:00
- **Afternoon 1**: 13:30 – 15:30
- **Afternoon 2**: 16:00 – 18:00

## Available Rooms

- **MSP Hall**: 150+ capacity (for Year 1 lectures)
- **Floor 0**: C0.004, C0.008, C0.016, C0.020, B0.001, B0.003 (75 capacity each)
- **Floor 1**: C1.005, C1.015 (75 capacity each)
- **Floor 2**: C2.007, C2.017 (75 capacity each)

## Project Structure

```
hackathon/
├── app.py                 # Flask application and routes
├── scheduler.py           # Scheduling algorithm
├── export.py              # PDF and Excel export functions
├── requirements.txt       # Python dependencies
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── input.html
│   └── schedule.html
├── static/
│   ├── schedule.css
│   └── example_input.json
└── data/
    └── schedules/         # Generated schedules stored here
```

## Hackathon Notes

### MVP Simplifications

- Single period only (no multi-period planning)
- No real-time schedule editing
- No user authentication
- Fixed room list
- TAs and HW assumed always available
- No elective course scheduling
- MSP hall always available

### Algorithm Details

The scheduler uses a **greedy constraint-based approach**:

1. Initialize empty schedule structure
2. For each course:
   - Schedule lectures first (theory before practical)
   - Then schedule tutorials (split into groups if >75 students)
   - Finally schedule labs (split into groups if >75 students)
3. For each session:
   - Find first available timeslot that satisfies:
     - Teacher is free
     - Program has no conflicts
     - Room is available with sufficient capacity
     - Year 1 lectures go to MSP

### Performance

- Typical runtime: 5-30 seconds for 2 programs with 6 courses
- Scales linearly with number of courses and sessions

## Future Enhancements

- Full CP-SAT or genetic algorithm for better optimization
- Real-time schedule editing and constraint checking
- Multi-period scheduling with holiday handling
- Master's program support
- Elective course handling
- Project room scheduling
- TA and equipment resource management
- Integration with university systems

## Credits

Developed during the Maastricht University Hackathon 2026

## License

MIT License - Free to use and modify
