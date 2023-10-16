import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import sqlite3
import pandas as pd
import csv
import dash_table
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)
# Initialize data variable outside of the callback
data = None

def create_database():
    conn = sqlite3.connect('apidata.db')
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
            client_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Define the layout with tabs
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Tab 1', value='tab1'),
        dcc.Tab(label='Tab 2', value='tab2'),
        dcc.Tab(label='Tab 3', value='tab3'),
    ]),
    html.Div(id='tab-content')
])

# Function to load data from CSV and insert into SQLite
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
            
            # Insert data into the SQLite database
            conn = sqlite3.connect('apidata.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (month, year, clientid, mal_code, uri, count, business_function, client_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (month, year, clientid, mal_code, uri, count, business_function, client_name))
            conn.commit()
            conn.close()

# Sample CSS style for basic formatting
app.css.append_css({
    'external_url': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'
})

# Define the layout with tabs
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Tab 1', value='tab1'),
        dcc.Tab(label='Tab 2', value='tab2'),
        dcc.Tab(label='Tab 3', value='tab3'),
    ]),
    html.Div(id='tab-content')
])

# Sample CSS style for basic formatting
app.css.append_css({
    'external_url': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'
})

@app.callback(Output('tab-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    global data  # Access the global data variable
    if tab == 'tab1':
        return html.Div([
            dcc.Dropdown(id='client-dropdown', options=[{'label': name, 'value': name} for name in get_client_names()]),
            dcc.Dropdown(id='function-dropdown', options=[{'label': func, 'value': func} for func in get_business_functions()]),
            dcc.Graph(id='line-graph')
        ])
    elif tab == 'tab2':
        return html.Div('Tab 2 Content')
    #global data  # Access the global data variable
    elif tab == 'tab3':
        if data is None:
            # Query the SQLite database to fetch all transactions
            conn = sqlite3.connect('apidata.db')
            query = "SELECT * FROM transactions"
            data = pd.read_sql(query, conn)

        return html.Div([
            dcc.Input(id='search-input', type='text', placeholder='Search Client, Function, Month, Year'),
            dash_table.DataTable(
                id='table',
                columns=[{'name': col, 'id': col} for col in data.columns],
                data=data.to_dict('records'),
                page_current=0,
                page_size=10,
            )
        ])
    else:
        return html.Div()

    
def get_client_names():
    conn = sqlite3.connect('apidata.db')
    query = "SELECT DISTINCT client_name FROM transactions"
    data = pd.read_sql(query, conn)
    return data['client_name'].tolist()

def get_business_functions():
    conn = sqlite3.connect('apidata.db')
    query = "SELECT DISTINCT business_function FROM transactions"
    data = pd.read_sql(query, conn)
    return data['business_function'].tolist()

@app.callback(Output('line-graph', 'figure'), [Input('client-dropdown', 'value'), Input('function-dropdown', 'value')])
def update_line_graph(selected_client, selected_function):
    conn = sqlite3.connect('apidata.db')
    query = f"SELECT month, year, SUM(count) as total_count FROM transactions WHERE client_name = '{selected_client}' AND business_function = '{selected_function}' GROUP BY month, year"
    data = pd.read_sql(query, conn)
    
    fig = px.line(data, x='month', y='total_count', title=f'Total Count of Transactions for {selected_client} - {selected_function}', markers=True)
    return fig



# Add a callback to update the table based on search input and pagination for Tab 3
# Add a callback to update the table based on search input and pagination for Tab 3
@app.callback(
    Output('table', 'data'),
    Output('table', 'page_current'),
    [Input('search-input', 'value')],
    [Input('table', 'page_current')],
    [State('table', 'data')],
    [State('tabs', 'value')]
)
def update_table(search_value, page_current, current_data, tab_value):
    if tab_value == 'tab3':
        if search_value is None:
            search_value = ''

        # Split the search value into individual search terms
        search_terms = search_value.split()

        # Create a list to store parameterized conditions for filtering
        conditions = []

        # Create a list to store the values to be used in the parameterized query
        values = []

        if search_terms:
            for term in search_terms:
                conditions.append("(client_name LIKE ? OR business_function LIKE ? OR month LIKE ? OR year LIKE ?)")
                values.extend(['%' + term + '%' for _ in range(4)])

            # Join the conditions with 'OR' to filter based on any of the search terms
            sql_condition = ' OR '.join(conditions)

            # Filter the data based on the parameterized query
            filtered_data = data.query(sql_condition, values=values)
        else:
            filtered_data = data  # No search terms, so no filtering

        return filtered_data.iloc[page_current * 10:(page_current + 1) * 10].to_dict('records'), page_current
    else:
        return dash.no_update

if __name__ == '__main__':
    create_database()
    csv_file = 'data.csv'  # Change this to your CSV file path
    load_data_from_csv(csv_file)
    app.run_server(debug=True)
