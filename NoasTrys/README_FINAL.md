# 🎓 Final Course Scheduling Solution

Your complete, optimized course scheduling system with all features working!

## ✨ Features

1. **✅ Tutorials get 2 rooms** - Each tutorial session is assigned 2 rooms
   - Preferably at the same time (minimized penalty)
   - Can be at different times if necessary

2. **✅ Lecturer unavailability WORKING** 
   - Properly respects all lecturer unavailable days
   - Verified in the output

3. **✅ Early morning penalty (08:30)**
   - Lectures at 08:30 are penalized (weight 100)
   - Tutorials at 08:30 are NOT penalized
   - Solver will minimize early morning lectures

4. **✅ Beautiful visualizations**
   - Interactive HTML calendar
   - Text-based views (by day, lecturer, room)
   - Export to HTML file
   - Export to Excel

---

## 🚀 Quick Start

### Run the complete notebook:

```bash
jupyter notebook FINAL_Complete_Solution.ipynb
```

Then just **"Run All Cells"** - that's it!

---

## 📊 What You'll Get

### 1. Console Output
- Model building progress
- Solver status
- Objective value (total penalties)
- Summary statistics

### 2. In-Notebook Visualizations
- **Weekly schedule** - all sessions organized by day
- **Grid view** - see all rooms at each time slot
- **Lecturer schedules** - when each professor teaches
- **Room utilization** - how each room is used

### 3. Interactive HTML Calendar
Displays right in the notebook with:
- Color-coded courses
- Hover-friendly cards
- Professional layout

### 4. Verification Checks
- ✅ Tutorial room assignments (2 rooms each)
- ✅ Early morning analysis (lectures vs tutorials)
- ✅ Lecturer unavailability verification

### 5. Exported Files
- **`course_schedule.html`** - Standalone HTML file you can open in any browser
- **`course_schedule.xlsx`** - Excel spreadsheet for further analysis

---

## 🌐 How to Open HTML in Browser

After running the notebook, you'll have a file called `course_schedule.html`.

### Option 1: Double-click
Just double-click the file in Finder (Mac) or File Explorer (Windows)

### Option 2: From Jupyter
Add this cell at the end:
```python
!open course_schedule.html  # Mac
# or
!start course_schedule.html  # Windows
```

### Option 3: Manual
1. Right-click `course_schedule.html`
2. Open With → Chrome/Safari/Firefox

The HTML file will open in a new browser tab with the full interactive calendar!

---

## 🔧 Files Included

| File | Purpose |
|------|---------|
| `FINAL_Complete_Solution.ipynb` | **Main file - run this!** |
| `final_model.py` | Model building logic |
| `visualize_schedule.py` | Visualization functions |
| `load_parameters.py` | Your original parameter loader |

---

## 📝 Model Details

### Decision Variables
- **x[c,i,r,d,t]**: Main scheduling variable (1 if session scheduled)
- **y[c,i,d,t]**: Tutorial timing helper (1 if tutorial at this time)

### Objective Function
Minimize:
```
100 × (early morning lectures) + 10 × (tutorial time splits)
```

### Constraints
1. **Sessions scheduled**: Lectures get 1 room, tutorials get 2 rooms
2. **Room capacity**: ≥50% for lectures, ≥25% per room for tutorials
3. **No room conflicts**: Max 1 session per room per timeslot
4. **Lecturer unavailability**: No teaching on unavailable days
5. **No lecturer conflicts**: Can't teach multiple sessions simultaneously
6. **No student conflicts**: Program students can't have overlapping sessions
7. **Chronological order**: Sessions happen in sequence

---

## 🎯 Understanding the Output

### Objective Value
Lower is better! Example:
- Objective = 500 means:
  - 5 early morning lectures (5 × 100 = 500), OR
  - 50 split tutorials (50 × 10 = 500), OR
  - Some combination

### Tutorial Assignments
Look for:
- ✅ **SAME TIME** - both rooms at same time (optimal!)
- ⚠️ **DIFFERENT TIMES** - rooms at different times (acceptable but penalized)

### Early Morning Analysis
Shows:
- 📚 Lectures at 08:30 (penalized)
- ✏️ Tutorials at 08:30 (not penalized)

### Lecturer Unavailability
Verifies each lecturer's constraints:
- ✅ **Not scheduled** - respect unavailability (good!)
- ❌ **VIOLATION** - teaching when unavailable (should never happen!)

---

## 🐛 Troubleshooting

### "Model is infeasible"
The constraints are too tight. Try:
- Reducing tutorial room requirement to 1
- Removing some unavailability constraints
- Adding more rooms or time slots

### "No unavailability constraints added"
Check that `params['U']` has data:
```python
print(params['U'])
```
Should show lecturer names with unavailable days.

### "Can't visualize schedule"
Model needs to solve successfully first. Check:
```python
print(f"Status: {pulp.LpStatus[status]}")
```
Should say "Optimal".

---

## 💡 Tips

### To prioritize same-time tutorials
Increase the penalty in `final_model.py`:
```python
tutorial_split_penalty += 50 * pulp.lpSum(...)  # Change 10 to 50
```

### To reduce early morning lectures more
Increase the penalty:
```python
early_morning_penalty = pulp.lpSum(
    200 * x[c, i, r, 1, 1]  # Change 100 to 200
    ...
)
```

### To allow tutorials at different times
Just reduce or remove the tutorial penalty (set to 0).

---

## 🎉 You're All Set!

Just run the notebook and enjoy your perfectly scheduled courses!

Questions? Check the verification cells to understand what the model did.

Happy scheduling! 📅✨
