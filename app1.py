import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Create a SQLite database and connect to it
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Create a table to store the data if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project TEXT,
        role TEXT,
        resource_name TEXT,
        api_name TEXT,
        api_endpoint TEXT,
        planned_sit_date TEXT,
        actual_sit_date TEXT,
        planned_pat_date TEXT,
        actual_pat_date TEXT,
        defects INTEGER,
        code_coverage REAL,
        promotion_failures INTEGER,
        code_review_comments INTEGER
    )
''')
conn.commit()
conn.close()

@app.route('/')
def index():
    # Initialize an empty list to store the data dictionaries
    data = []

    # Fetch data from the database and convert each row into a dictionary
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM data')
    
    # Fetch the column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]
    
    for row in cursor.fetchall():
        data_dict = {}  # Create an empty dictionary for each row
        for i, column in enumerate(column_names):
            data_dict[column] = row[i]  # Assign each column value to the corresponding key
        data.append(data_dict)  # Append the dictionary to the list

    conn.close()
    # Calculate average code coverage per resource name
    avg_code_coverage_data = {}
    print('--------------',data)
    for row in data:
        resource_name = row['resource_name']
        code_coverage = row['code_coverage']
        if resource_name not in avg_code_coverage_data:
            avg_code_coverage_data[resource_name] = []
        avg_code_coverage_data[resource_name].append(code_coverage)

    avg_code_coverage = {}
    for resource_name, code_coverage_values in avg_code_coverage_data.items():
        avg = sum(code_coverage_values) / len(code_coverage_values)
        avg_code_coverage[resource_name] = avg

    # Calculate the number of rows that have exceeded the timeline
    exceeded_timeline_count = 0
    for row in data:
        planned_sit_date = row['planned_sit_date']
        actual_sit_date = row['actual_sit_date']
        if planned_sit_date and actual_sit_date and actual_sit_date > planned_sit_date:
            exceeded_timeline_count += 1

    return render_template('index.html', data=data, avg_code_coverage=avg_code_coverage, exceeded_timeline_count=exceeded_timeline_count)

@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        print('hello...')
        # Get data from the form
        project = request.form['project']
        role = request.form['role']
        resource_name = request.form['resource_name']
        api_name = request.form['api_name']
        api_endpoint = request.form['api_endpoint']
        planned_sit_date = request.form['planned_sit_date']
        actual_sit_date = request.form['actual_sit_date']
        planned_pat_date = request.form['planned_pat_date']
        actual_pat_date = request.form['actual_pat_date']
        defects = int(request.form['defects'])
        code_coverage = float(request.form['code_coverage'])
        promotion_failures = int(request.form['promotion_failures'])
        code_review_comments = int(request.form['code_review_comments'])
    
        # Insert data into the database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO data (project, role, resource_name, api_name, api_endpoint, planned_sit_date,
                              actual_sit_date, planned_pat_date, actual_pat_date, defects, code_coverage,
                              promotion_failures, code_review_comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project, role, resource_name, api_name, api_endpoint, planned_sit_date, actual_sit_date,
              planned_pat_date, actual_pat_date, defects, code_coverage, promotion_failures,
              code_review_comments))
        print('hello...2')
        conn.commit()
        conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
