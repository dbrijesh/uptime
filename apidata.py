import sqlite3
import pandas as pd
from flask import Flask, render_template, request, jsonify
import plotly.express as px
import csv

app = Flask(__name__)

# Function to load data from CSV into SQLite
def create_database():
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE transactions')
    conn.commit()
    # Create the table with the necessary columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            month INTEGER,
            year INTEGER,
            clientid TEXT,
            mal_code TEXT,
            uri TEXT,
            count INTEGER,
            business_function TEXT,
            client_name TEXT,
            date TEXT  -- Add a date column to store 'YYYY-MM'
        )
    ''')
    conn.commit()
    conn.close()

def load_data_from_csv(csv_file):
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            month = row['month']
            year = row['year']
            clientid = row['clientid']
            mal_code = row['mal_code']
            uri = row['uri']
            count = int(row['count'])
            business_function = row['uri']   # Replace with actual data
            client_name =  row['clientid']# Replace with actual data
            date = f"{year}-{month.zfill(2)}"  # Combine year and month
            print(date)
            # Insert data into the SQLite database
            conn = sqlite3.connect('transactions.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (month, year, clientid, mal_code, uri, count, business_function, client_name, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (month, year, clientid, mal_code, uri, count, business_function, client_name, date))
            conn.commit()
            cursor.execute('''
                SELECT date, SUM(count) as total_count, client_name, business_function
                FROM transactions
                GROUP BY date, client_name, business_function
                ORDER BY date
            ''')
            print('hii->',cursor.fetchall())
            conn.close()



# Define a route to display the HTML page
@app.route('/')
def index():
    conn = sqlite3.connect('transactions.db')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT client_name FROM transactions")
    client_names = [row[0] for row in cur.fetchall()]
    print(client_names)
    cur.execute("SELECT DISTINCT business_function FROM transactions")
    business_functions = [row[0] for row in cur.fetchall()]
    conn.close()
    months = [("1", "Jan"), ("2", "Feb"), ("3", "Mar"), ("4", "Apr"), ("5", "May"), ("6", "Jun"), ("7", "Jul"), ("8", "Aug"), ("9", "Sep"), ("10", "Oct"), ("11", "Nov"), ("12", "Dec")]
    years = ["2023", "2024", "2025", "2026"]
    return render_template('index.html', client_names=client_names, business_functions=business_functions,months=months, years=years)

# Define a route to fetch data for the line graph
@app.route('/get_data', methods=['POST'])
def get_data():
    start_month = request.form['start_month']
    start_year = request.form['start_year']
    end_month = request.form['end_month']
    end_year = request.form['end_year']
    selected_client_names = request.form.getlist('client_name')
    selected_business_functions = request.form.getlist('business_function')

    conn = sqlite3.connect('transactions.db')

    query = """
    SELECT date, SUM(count) as total_count, client_name, business_function
    FROM transactions
    WHERE client_name IN ({})
    AND business_function IN ({})
    AND date BETWEEN ? AND ?
    GROUP BY date, client_name, business_function
    ORDER BY date
    """.format(','.join(['?'] * len(selected_client_names)), ','.join(['?'] * len(selected_business_functions)))

    start_date = f"{start_year}-{start_month.zfill(2)}"
    end_date = f"{end_year}-{end_month.zfill(2)}"

    params = selected_client_names + selected_business_functions + [start_date, end_date]

    data = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Convert the date string 'YYYY-MM' to a more readable text format
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%b %Y')

    return data.to_json(orient='split')

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    print('hrllo')
    print(request)
    try:
        file = request.files['csv-file']
        print(file.filename)
        
        
        if not file or file.filename == '':
            return "No file selected."

        if not file.filename.endswith('.csv'):
            return "Invalid file format. Please upload a CSV file."

        # Read the uploaded CSV file into a Pandas DataFrame
        df = pd.read_csv(file)
        print(df)
        
        # Check for specific columns in the DataFrame
        if 'clientid' in df.columns and 'client_name' in df.columns:
            print('if bloc 1')
            # Update client names based on clientid
            for index, row in df.iterrows():
                client_id = row['clientid']
                new_client_name = row['client_name']
                update_client_name(client_id, new_client_name)

        elif 'uri' in df.columns and 'business_function' in df.columns:
            # Update business functions based on uri
            print('if bloc 2')
            for index, row in df.iterrows():
                uri = row['uri']
                new_business_function = row['business_function']
                update_business_function(uri, new_business_function)

        elif 'month' in df.columns and 'year' in df.columns:
            print('if bloc 3')
            for index, row in df.iterrows():
                # Implement logic to insert new data based on your requirements
                month = row['month']
                year = row['year']
                clientid = row['clientid']
                mal_code = row['mal_code']
                uri = row['uri']
                count = int(row['count'])
                business_function = row['uri']   # Replace with actual data
                client_name =  row['clientid']# Replace with actual data
                date = f"{year}-{month.zfill(2)}"  # Combine year and month
                print(date)
                conn = sqlite3.connect('transactions.db')
                cursor = conn.cursor()
                # Insert data into the SQLite database 
                cursor.execute('''
                    INSERT INTO transactions (month, year, clientid, mal_code, uri, count, business_function, client_name, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (month, year, clientid, mal_code, uri, count, business_function, client_name, date))
                conn.commit()
                conn.close()
                pass
        

        return "CSV file processed successfully."

    except Exception as e:
        return "Error: " + str(e)

def update_client_name(client_id, new_client_name):
    # Implement logic to update client names in your database
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    # Insert data into the SQLite database 
    cursor.execute('''
        UPDATE  transactions client_name = ? WHERE client_id = ?
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (new_client_name,client_id))
    conn.commit()
    conn.close()
    pass

def update_business_function(uri, new_business_function):
    # Implement logic to update business functions in your database
    pass


@app.route('/get_transactions', methods=['POST'])
def get_transactions():
   

    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()

    query = """
    SELECT date, client_name, business_function, count
    FROM transactions    
    """
    
 

    cursor.execute(query)
    data = cursor.fetchall()

    conn.close()

    result = []
    for row in data:
        result.append({
            'date': row[0],
            'client_name': row[1],
            'business_function': row[2],
            'count': row[3]
            # Add other columns as needed
        })

    return jsonify({'data': result})

if __name__ == '__main__':
    create_database()
    csv_file = 'data.csv'  # Change this to your CSV file path
    load_data_from_csv(csv_file)
    app.run(debug=True)
