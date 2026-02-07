from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import json
import os
from datetime import datetime
from scheduler import generate_schedule
from export import export_to_pdf, export_to_excel

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'data/schedules'

# Ensure data directory exists
os.makedirs('data/schedules', exist_ok=True)

@app.route('/')
def index():
    """Landing page with navigation"""
    return render_template('index.html')

@app.route('/input', methods=['GET', 'POST'])
def input_page():
    """JSON upload and validation interface - NOW SIMPLIFIED"""
    if request.method == 'POST':
        # Generate schedule directly from the JSON files in static/
        try:
            # Generate schedule
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            schedule_data = generate_schedule({
                'metadata': {
                    'period': 'Period 2',
                    'year': '2024-2025',
                    'weeks': 1,
                    'start_date': '2025-10-27'
                }
            })
            
            # Save schedule
            schedule_filename = f'schedule_{timestamp}.json'
            schedule_filepath = os.path.join(app.config['UPLOAD_FOLDER'], schedule_filename)
            
            with open(schedule_filepath, 'w') as f:
                json.dump(schedule_data, f, indent=2)
            
            return jsonify({
                'success': True,
                'schedule_id': timestamp,
                'message': 'Schedule generated successfully!'
            })
        except Exception as e:
            return jsonify({'error': f'Schedule generation failed: {str(e)}'}), 500
    
    return render_template('input.html')

@app.route('/schedule/<schedule_id>')
def view_schedule(schedule_id):
    """View generated schedule"""
    schedule_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'schedule_{schedule_id}.json')
    
    if not os.path.exists(schedule_filepath):
        return "Schedule not found", 404
    
    with open(schedule_filepath, 'r') as f:
        schedule_data = json.load(f)
    
    return render_template('schedule.html', schedule=schedule_data, schedule_id=schedule_id)

@app.route('/schedule/<schedule_id>/<program>')
def view_program_schedule(schedule_id, program):
    """View schedule filtered by program"""
    schedule_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'schedule_{schedule_id}.json')
    
    if not os.path.exists(schedule_filepath):
        return "Schedule not found", 404
    
    with open(schedule_filepath, 'r') as f:
        schedule_data = json.load(f)
    
    # Filter schedule for specific program
    filtered_schedule = filter_schedule_by_program(schedule_data, program)
    
    return render_template('schedule.html', schedule=filtered_schedule, schedule_id=schedule_id, program=program)

@app.route('/export/pdf/<schedule_id>/<program>')
def export_pdf(schedule_id, program):
    """Export schedule as PDF"""
    schedule_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'schedule_{schedule_id}.json')
    
    if not os.path.exists(schedule_filepath):
        return "Schedule not found", 404
    
    with open(schedule_filepath, 'r') as f:
        schedule_data = json.load(f)
    
    # Filter for program
    filtered_schedule = filter_schedule_by_program(schedule_data, program)
    
    # Generate PDF
    pdf_path = export_to_pdf(filtered_schedule, program, schedule_id)
    
    return send_file(pdf_path, as_attachment=True, download_name=f'{program}_schedule.pdf')

@app.route('/export/excel/<schedule_id>/<program>')
def export_excel(schedule_id, program):
    """Export schedule as Excel"""
    schedule_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'schedule_{schedule_id}.json')
    
    if not os.path.exists(schedule_filepath):
        return "Schedule not found", 404
    
    with open(schedule_filepath, 'r') as f:
        schedule_data = json.load(f)
    
    # Filter for program
    filtered_schedule = filter_schedule_by_program(schedule_data, program)
    
    # Generate Excel
    excel_path = export_to_excel(filtered_schedule, program, schedule_id)
    
    return send_file(excel_path, as_attachment=True, download_name=f'{program}_schedule.xlsx')

@app.route('/example')
def download_example():
    """Download example JSON template"""
    return send_file('static/example_input.json', as_attachment=True)

def filter_schedule_by_program(schedule_data, program):
    """Filter schedule to show only classes for a specific program"""
    filtered = {
        'metadata': schedule_data.get('metadata', {}),
        'programs': {program: schedule_data['programs'].get(program, {})},
        'schedule': {}
    }
    
    program_courses = schedule_data['programs'].get(program, {}).get('courses', [])
    
    for week, week_data in schedule_data.get('schedule', {}).items():
        filtered['schedule'][week] = {}
        for day, day_data in week_data.items():
            filtered['schedule'][week][day] = {}
            for timeslot, sessions in day_data.items():
                # Filter sessions that are relevant to this program
                relevant_sessions = [s for s in sessions if s.get('course') in program_courses or s.get('program') == program]
                if relevant_sessions:
                    filtered['schedule'][week][day][timeslot] = relevant_sessions
    
    return filtered

if __name__ == '__main__':
    app.run(debug=True, port=5000)
