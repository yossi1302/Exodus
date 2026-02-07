# FSP Course Scheduler - Quick Start Guide

## What You've Built

A complete MVP for automated course scheduling with:
- ✅ JSON input interface for uploading requirements
- ✅ Constraint-based scheduler that satisfies all hard constraints
- ✅ Interactive web viewer with program filtering
- ✅ PDF and Excel export functionality
- ✅ Professional UI matching university branding

## How to Run

### 1. Start the Server

```bash
cd "/Users/yossi1302/Documents/Maastricht_University/2025 - 2026/Hackathon"
python3 app.py
```

Server runs at: **http://localhost:5000**

### 2. Access the Application

Open your browser and go to `http://localhost:5000`

### 3. Create a Schedule

**Option A: Use Example Template**
1. Click "Create New Schedule"
2. Click "Download Example"
3. Upload the example JSON
4. Wait 5-30 seconds for generation
5. View your schedule

**Option B: Create Custom JSON**
1. Create a JSON file with your requirements (see format below)
2. Upload via "Create Schedule" page
3. Schedule generates automatically

## JSON Input Structure

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
    "E. Smirnov": {
      "courses": ["BCS1220"],
      "unavailable": ["Monday-08:30"]
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

## Features Demo

### 1. View Generated Schedule
- Schedules displayed in week-by-week tables
- Color-coded by session type (lectures, tutorials, labs)
- Hover over sessions to highlight same course across weeks

### 2. Filter by Program
- Use dropdown to view schedule for specific program
- Shows only courses relevant to that program
- Useful for student timetables

### 3. Export Options
- **PDF**: Professional layout matching original schedules
- **Excel**: Editable spreadsheet with formatting
- Downloaded files stored in `data/schedules/`

## Testing the System

### Test 1: Home Page
```bash
curl http://localhost:5000/
```
Should return HTML homepage

### Test 2: Example JSON Download
```bash
curl http://localhost:5000/example -o test_input.json
```

### Test 3: Generate Schedule (CLI)
```bash
cd "/Users/yossi1302/Documents/Maastricht_University/2025 - 2026/Hackathon"
python3 scheduler.py
```
Should output complete JSON schedule

## File Locations

- **Uploaded inputs**: `data/schedules/input_TIMESTAMP.json`
- **Generated schedules**: `data/schedules/schedule_TIMESTAMP.json`
- **Exported PDFs**: `data/schedules/schedule_PROGRAM_TIMESTAMP.pdf`
- **Exported Excel**: `data/schedules/schedule_PROGRAM_TIMESTAMP.xlsx`

## Hard Constraints (All Satisfied)

1. ✓ No teacher conflicts (teacher teaches one course at a time)
2. ✓ No student conflicts (program has one course at a time)
3. ✓ All required sessions scheduled
4. ✓ Teacher availability respected
5. ✓ Room capacity constraints (Year 1 → MSP hall)
6. ✓ Theory before practical (lectures before labs/tutorials)
7. ✓ 4 timeslots × 5 days × 7 weeks framework

## Soft Constraints (Optimized)

- Even distribution across the week
- Max 3 lectures per day
- Minimize student gaps
- Same course → same room
- Continuous class blocks

## Room Configuration

| Room | Capacity | Notes |
|------|----------|-------|
| MSP Hall | 150+ | Year 1 lectures only |
| C0.004, C0.008, C0.016, C0.020 | 75 | Floor 0 |
| C1.005, C1.015 | 75 | Floor 1 |
| C2.007, C2.017 | 75 | Floor 2 |
| B0.001, B0.003 | 75 | B Building |

## Timeslots

| Slot | Time |
|------|------|
| Morning 1 | 08:30 – 10:30 |
| Morning 2 | 11:00 – 13:00 |
| Afternoon 1 | 13:30 – 15:30 |
| Afternoon 2 | 16:00 – 18:00 |

## Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process if needed
kill -9 <PID>
```

### Import errors
```bash
# Reinstall dependencies
pip install --user Flask ortools deap reportlab openpyxl
```

### Schedule generation fails
- Check JSON format validity
- Ensure all courses have assigned teachers
- Verify program course lists match course codes
- Check for impossible constraints (e.g., too many required sessions)

## Next Steps for Hackathon Presentation

### Demo Flow
1. **Show Homepage** - Explain the problem
2. **Upload Example** - Show input format
3. **View Generated Schedule** - Highlight constraint satisfaction
4. **Filter by Program** - Show student perspective
5. **Export to PDF/Excel** - Show integration potential

### Key Talking Points
- Saves hours of manual scheduling work
- Guarantees all hard constraints
- Optimizes for student experience
- Easy to modify and re-generate
- Ready for integration with existing systems

### Live Demo Tips
- Have example JSON pre-loaded in browser
- Keep terminal open to show algorithm running
- Prepare comparison with manual PDF schedules
- Discuss scalability to full faculty schedule

## Known Limitations (MVP)

- Single period only
- No master's programs
- No elective scheduling
- No real-time editing
- Simplified soft constraint optimization
- No multi-objective optimization UI

## Future Enhancements

1. **Algorithm**: Full CP-SAT or genetic algorithm
2. **UI**: Drag-and-drop schedule editing
3. **Features**: Multi-period planning, holidays, exam scheduling
4. **Integration**: Connect to university systems
5. **Analytics**: Constraint violation reports, optimization metrics
6. **Collaboration**: Multi-user editing, version control

## Credits

Built for Maastricht University Hackathon 2026
Faculty of Science and Engineering

## Support

For issues or questions during the hackathon:
- Check README.md for detailed documentation
- Review example_input.json for format reference
- Test scheduler.py independently if Flask issues arise
