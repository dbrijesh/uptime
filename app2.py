import sqlite3
import dash
import csv
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import io
import base64

app = dash.Dash(__name__, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])

# Function to create an SQLite database and table (if not exists)
def create_database():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE data')
    conn.commit()
    # Create the table with the necessary columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            date TEXT,
            clientid TEXT,
            mal_code TEXT,
            uri TEXT,
            count INTEGER,
            business_function TEXT,
            client_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to load data from CSV and insert into SQLite
def load_data_from_csv(csv_file):
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            date = row['date']
            clientid = row['clientid']
            mal_code = row['mal_code']
            uri = row['uri']
            count = int(row['count'])
            business_function = row['uri']   # Replace with actual data
            client_name =  row['clientid']# Replace with actual data
            
            # Insert data into the SQLite database
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO data (date, clientid, mal_code, uri, count, business_function, client_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date, clientid, mal_code, uri, count, business_function, client_name))
            conn.commit()
            conn.close()


app.layout = html.Div([
    # Navbar
    html.Nav([
        html.A('BMW Dashboard', className='navbar-brand'),
        html.Button(type='button', className='navbar-toggler', **{'data-toggle': 'collapse', 'data-target': '#navbarNav'}),
        html.Div([
            html.Ul([
                html.Li(html.A('Home', className='nav-link', href='#')),
                html.Li(html.A('About', className='nav-link', href='#')),
                html.Li(html.A('Contact', className='nav-link', href='#')),
            ], className='navbar-nav ml-auto')
        ], className='collapse navbar-collapse', id='navbarNav')
    ], className='navbar navbar-expand-lg navbar-dark bg-dark'),

    # Content Container
    html.Div([
        html.H1('API Usage Metrics', className='mt-5'),
       
       # Date range input form with improved styling
        # Date range input form with minimal divs
        # Date range input form with improved styling
        html.Div([
           
            html.Label('Start Date:', className='mr-2'),
            html.Label(' ', className='mr-2'),
            dcc.DatePickerSingle(id='start-date-picker', date='2023-01-01'),
            html.Label(' ', className='mr-2'),

                            
            html.Label('End Date:', className='mr-2'),
            html.Label(' ', className='mr-2'),
            dcc.DatePickerSingle(id='end-date-picker', date='2023-12-31'),
            html.Label(' ', className='mr-2'),

            html.Button('Generate Graphs', id='generate-button', className='btn btn-primary mr-2'),

           
        ]),


        # Tabs
        dcc.Tabs(id='tabs', value='tab-1', children=[
            dcc.Tab(label='Graph 1', value='tab-1'),
            dcc.Tab(label='Graph 2', value='tab-2'),
        ], className='mt-4'),
        
        html.Div(id='tabs-content'),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files For Uploading Data')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'verticalAlign': 'middle'
            },
            multiple=False  # Allow only one file to be uploaded
        ),
        html.Div(id='upload-status',className='navbar-brand'),
        # Placeholder for the graph output
    ], className='container mt-4'),
    
])

# Callback to handle file upload and update the database
@app.callback(
    Output('upload-status', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_database_with_csv(contents, filename):
    if contents is None:
        return None

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    print('decoded',decoded)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    print('df',df)
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    if 'clientid' in df.columns and 'client_name' in df.columns:
        # Check if the file contains 'clientid' and 'client_name' columns
        for index, row in df.iterrows():
            clientid = row['clientid']
            client_name = row['client_name']
            cursor.execute('''
                UPDATE data
                SET client_name = ?
                WHERE clientid = ?
            ''', (client_name, clientid))
    else:
        # If not, update all fields for the entire data table
        #cursor.execute('DELETE FROM data')  # Clear existing data
        for index, row in df.iterrows():
            cursor.execute('''
                INSERT INTO data (date, clientid, mal_code, uri, count, business_function, client_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['date'],
                row['clientid'],
                row['mal_code'],
                row['uri'],
                row['count'],
                row['uri'],
                row['clientid']
            ))

    conn.commit()
    conn.close()

    return html.Div(f'Updated {len(df)} records with client names from CSV file: {filename}',style={'text-align': 'center','font-size': '14px','verticalAlign': 'middle'})



@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    Input('generate-button', 'n_clicks'),
    Input('start-date-picker', 'date'),
    Input('end-date-picker', 'date')
)
def render_content(tab, n_clicks, start_date, end_date):
    if n_clicks is None:
        return
    
    # Fetch data from the database based on date range
    conn = sqlite3.connect('data.db')
    query = f'''
        SELECT strftime('%Y-%m', date) AS month, client_name, business_function, SUM(count) as total_count
        FROM data
        WHERE date BETWEEN ? AND ?
        GROUP BY month, client_name, business_function
    '''
    data = conn.execute(query, (start_date, end_date)).fetchall()
    print(data)

    if tab == 'tab-1':
        # Render the updated first graph
        return dcc.Graph(figure=generate_graph1(data))
    elif tab == 'tab-2':
        # Render the second graph
        return dcc.Graph(figure=generate_graph2(data))

# Function to generate the updated first graph
def generate_graph1(data):
    df = pd.DataFrame(data, columns=['month', 'client_name', 'business_function', 'total_count'])
    
    fig = go.Figure()

    for client_name in df['client_name'].unique():
        print(client_name)
        client_data = df[df['client_name'] == client_name]
        for function_name in client_data['business_function'].unique():
            function_data = client_data[client_data['business_function'] == function_name]
            fig.add_trace(go.Scatter(
                x=client_data['month'],
                y=function_data['total_count'],
                mode='lines+markers',
                name=f'{client_name} - {function_name}'
            ))
    
    fig.update_layout(title='Monthly Total Count by Client Name and Business Function', xaxis_title='Month', yaxis_title='Total Count')
    
    return fig

# Function to generate the second graph
def generate_graph2(data):
    df = pd.DataFrame(data, columns=['month', 'client_name', 'business_function', 'total_count'])
    
    # Create a color scale mapping each unique client name to a different color
    color_scale = {client_name: 'rgb({}, {}, {})'.format(
        int(255 * (i / len(df['client_name'].unique()))),
        int(100 + 155 * (i / len(df['client_name'].unique()))),
        int(100 + 155 * (i / len(df['client_name'].unique())))
    ) for i, client_name in enumerate(df['client_name'].unique())}
    
    fig = go.Figure()
    
    # Use a dictionary to store unique legend names for each client
    legend_names = {}
    
    for month in df['month'].unique():
        month_data = df[df['month'] == month]
        for client_name in month_data['client_name'].unique():
            client_data = month_data[month_data['client_name'] == client_name]
            total_count = client_data['total_count'].sum()
            
            # Create a unique legend name for each client based on just the client name
            if client_name not in legend_names:
                legend_names[client_name] = f'{client_name}-{month}'
            
            fig.add_trace(go.Bar(
                x=[month],
                y=[total_count],
                name=legend_names[client_name],
                marker=dict(color=color_scale[client_name])
            ))
    
    fig.update_layout(title='Total Count by Client Name for Each Month', xaxis_title='Month', yaxis_title='Total Count')
    
    return fig

if __name__ == '__main__':
    create_database()
    csv_file = 'data.csv'  # Change this to your CSV file path
    load_data_from_csv(csv_file)
    app.run_server(debug=True)
