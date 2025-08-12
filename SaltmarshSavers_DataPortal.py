import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate

print("All imports successful")  # DEBUG

# Define the path to the directory containing the Excel files
data_dir = os.path.join(os.path.dirname(__file__), 'data')

# ADD THESE DEBUG PRINTS:
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {os.path.dirname(__file__)}")
print(f"Data directory: {data_dir}")
print(f"Data directory exists: {os.path.exists(data_dir)}")

# Image mapping for displaying images based on clicked labels
image_mapping = {
    'Altered Hydrology (Tidal)': '/assets/Altered Hydrology (Tidal).png',
    #'Threat 2': '/assets/threat2.png',
    #'Value 1': '/assets/value1.png',
    #'Value 2': '/assets/value2.png',
    # Add more mappings as needed
}

# MOVED THIS LINE UP - Define years BEFORE using it
years = [2021, 2022, 2023, 2024]  # Add more years as needed
print(f"Years defined: {years}")  # DEBUG

# Load the Excel data from multiple files and add a column to identify the year
data_frames = []
for year in years:
    file_path = os.path.join(data_dir, f'data_{year}.xlsx')
    print(f"Looking for file: {file_path}")  # DEBUG
    print(f"File exists: {os.path.exists(file_path)}")  # DEBUG
    
    if not os.path.exists(file_path):
        print(f"WARNING: File not found: {file_path}")
        continue
        
    try:
        sheet_names = pd.ExcelFile(file_path).sheet_names
        for sheet in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet).assign(Year=year, Sheet=sheet)
            data_frames.append(df)
    except Exception as e:
        print(f"ERROR reading {file_path}: {e}")
        continue

if not data_frames:
    print("ERROR: No data files were loaded!")
    # Create empty dataframe with required columns to prevent crashes
    data = pd.DataFrame(columns=['Location', 'Latitude', 'Longitude', 'Year', 'Sheet', 'TVR', 'Threat Score', 'Value Score'])
else:
    data = pd.concat(data_frames, ignore_index=True)
    print(f"Data Loaded:\n{data.head()}")

# Convert empty strings to NaN in Latitude and Longitude columns
data['Latitude'] = pd.to_numeric(data['Latitude'], errors='coerce')
data['Longitude'] = pd.to_numeric(data['Longitude'], errors='coerce')

# Filter out rows with missing latitude/longitude values for map calculations
map_data = data.dropna(subset=['Latitude', 'Longitude'])
print(f"Map data points (after removing NaN): {len(map_data)}")

# Calculate the bounding box of the data points - with fallback for empty data
if len(map_data) > 0:
    min_lat = map_data['Latitude'].min()
    max_lat = map_data['Latitude'].max()
    min_lon = map_data['Longitude'].min()
    max_lon = map_data['Longitude'].max()
    
    # Calculate the center of the map based on the bounding box
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
else:
    # Default to Australia coordinates if no data
    min_lat, max_lat = -45.0, -10.0
    min_lon, max_lon = 110.0, 155.0
    center_lat = -25.0
    center_lon = 135.0
    print("No map data found - using default Australia coordinates")

# Calculate the zoom level based on the bounding box
def calculate_zoom(min_lat, max_lat, min_lon, max_lon):
    lat_diff = max_lat - min_lat
    lon_diff = max_lon - min_lon
    max_diff = max(lat_diff, lon_diff)
    zoom = 8 - (max_diff * 10)  # Adjust the multiplier as needed
    return max(1, min(zoom, 15))  # Ensure zoom level is within a reasonable range

zoom_level = calculate_zoom(min_lat, max_lat, min_lon, max_lon)

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
])

# Enhanced custom CSS with your original styling preserved
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .main-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            margin: 100px 20px 80px 20px;
            overflow: hidden;
            animation: fadeInUp 0.8s ease-out;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 2px solid transparent;
            background-clip: padding-box;
        }
        
        .stat-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border-color: rgba(46, 139, 87, 0.3);
        }
        
        .stat-card:nth-child(1) { animation-delay: 0.1s; }
        .stat-card:nth-child(2) { animation-delay: 0.2s; }
        .stat-card:nth-child(3) { animation-delay: 0.3s; }
        .stat-card:nth-child(4) { animation-delay: 0.4s; }
        
        @keyframes countUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .stat-card {
            animation: countUp 0.6s ease-out both;
        }
        
        .chart-enhanced {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            overflow: hidden;
        }
        
        .chart-enhanced:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }
        
        @media (max-width: 1200px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .main-container {
                margin: 80px 10px 60px 10px;
                border-radius: 15px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define the layout of the app
app.layout = html.Div([
    # Fixed Header (your original)
    html.Header([
        html.Div([
            html.H1("Saltmarsh Savers", style={
                'color': 'white',
                'font-family': 'Inter, sans-serif',
                'font-size': '24px',
                'margin': '0',
                'font-weight': '600'
            })
        ], style={
            'display': 'flex',
            'align-items': 'center',
            'justify-content': 'center',
            'width': '100%',
            'position': 'relative'
        }),
        html.Div(style={
            'position': 'absolute',
            'left': '20px',
            'top': '50%',
            'transform': 'translateY(-50%)'
        }, children=[
            html.Img(src='/assets/logo.png', style={
                'height': '60px'
            })
        ])
    ], style={
        'backgroundColor': '#253746',
        'textAlign': 'center',
        'padding': '1em 0',
        'height': '80px',
        'position': 'fixed',
        'width': '100%',
        'top': '0',
        'left': '0',
        'zIndex': '1000',
    }),

    # Main Container
    html.Div([
        # Stats Section at the top of main content
        html.Div([
            html.H2("Impact by the Numbers", style={
                'text-align': 'center',
                'color': '#2E8B57',
                'font-weight': '600',
                'margin-bottom': '30px',
                'font-size': '2rem'
            }),
            html.Div([
                # Stat Card 1
                html.Div([
                    html.Div([
                        html.I(className="fas fa-map-marker-alt", style={'font-size': '3rem', 'color': '#3CB371', 'margin-bottom': '15px'}),
                        html.H3(id="total-sites", children="0", style={'font-size': '3rem', 'margin': '0', 'color': '#2E8B57', 'font-weight': '700'}),
                        html.P("Saltmarsh Sites", style={'margin': '5px 0 0 0', 'color': '#666', 'font-size': '1.1rem', 'font-weight': '500'})
                    ], style={'text-align': 'center', 'padding': '30px 20px'})
                ], className='stat-card'),
                
                # Stat Card 2
                html.Div([
                    html.Div([
                        html.I(className="fas fa-calendar-alt", style={'font-size': '3rem', 'color': '#3CB371', 'margin-bottom': '15px'}),
                        html.H3(id="years-monitoring", children="0", style={'font-size': '3rem', 'margin': '0', 'color': '#2E8B57', 'font-weight': '700'}),
                        html.P("Years of Monitoring", style={'margin': '5px 0 0 0', 'color': '#666', 'font-size': '1.1rem', 'font-weight': '500'})
                    ], style={'text-align': 'center', 'padding': '30px 20px'})
                ], className='stat-card'),
                
                # Stat Card 3
                html.Div([
                    html.Div([
                        html.I(className="fas fa-exclamation-triangle", style={'font-size': '3rem', 'color': '#e74c3c', 'margin-bottom': '15px'}),
                        html.H3(id="avg-threats", children="0", style={'font-size': '3rem', 'margin': '0', 'color': '#2E8B57', 'font-weight': '700'}),
                        html.P("Avg Threat Score", style={'margin': '5px 0 0 0', 'color': '#666', 'font-size': '1.1rem', 'font-weight': '500'})
                    ], style={'text-align': 'center', 'padding': '30px 20px'})
                ], className='stat-card'),
                
                # Stat Card 4
                html.Div([
                    html.Div([
                        html.I(className="fas fa-leaf", style={'font-size': '3rem', 'color': '#27ae60', 'margin-bottom': '15px'}),
                        html.H3(id="avg-values", children="0", style={'font-size': '3rem', 'margin': '0', 'color': '#2E8B57', 'font-weight': '700'}),
                        html.P("Avg Value Score", style={'margin': '5px 0 0 0', 'color': '#666', 'font-size': '1.1rem', 'font-weight': '500'})
                    ], style={'text-align': 'center', 'padding': '30px 20px'})
                ], className='stat-card'),
            ], className='stats-grid'),
        ], style={'padding': '40px 30px', 'background': 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)', 'margin-bottom': '30px'}),

        # Charts Section (your original layout)
        html.Div([
            html.Div([
                dcc.Graph(id='map', style={'width': '100%', 'height': '100%', 'margin': '0', 'padding': '0'}),
            ], className='chart-enhanced', style={'width': '50%', 'height': '600px', 'minHeight': '600px', 'margin': '0', 'padding': '5px', 'overflow': 'hidden'}),
            html.Div([
                dcc.Graph(id='donut-chart', style={'width': '100%', 'height': '100%', 'margin': '0', 'padding': '0'}),
            ], className='chart-enhanced', style={'width': '25%', 'height': '600px', 'margin': '0', 'padding': '2px', 'boxSizing': 'border-box', 'overflow': 'hidden'}),
            html.Div([
                dcc.Graph(id='value-donut-chart', style={'width': '100%', 'height': '100%', 'margin': '0', 'padding': '0'})
            ], className='chart-enhanced', style={'width': '25%', 'height': '600px', 'margin': '0', 'padding': '2px', 'boxSizing': 'border-box', 'overflow': 'hidden'}),
        ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', 'height': '600px', 'flexShrink': '0', 'marginBottom': '25px', 'gap': '10px'}),

        # Year Slider Section
        html.Div([
            dcc.Slider(
                id='year-slider',
                min=min(years) if years else 2021,
                max=max(years) if years else 2024,
                value=max(years) if years else 2024,
                marks={str(year): {'label': str(year), 'style': {'font-size': '14px', 'font-family': 'Inter, sans-serif'}} for year in years},
                step=None
            )
        ], style={'width': '50%', 'margin': 'auto', 'background': 'white', 'border-radius': '15px', 'box-shadow': '0 10px 30px rgba(0, 0, 0, 0.1)', 'padding': '20px'}),

    ], className='main-container'),

    # Modal
    dbc.Modal([
        dbc.ModalBody([
            html.Img(id="modal-image", style={'width': '100%'})
        ]),
        dbc.ModalFooter(
            dbc.Button("Close", id="close", className="ml-auto")
        )
    ], id="modal", is_open=False),

    dcc.Store(id='stored-click-data'),

    # Footer (your original)
    html.Footer([
        html.P("", style={
            'color': 'white',
            'font-family': 'Inter, sans-serif',
            'font-size': '12px',
            'margin': '0'
        }),
        html.Button("Contact us", style={
            'backgroundColor': 'transparent',
            'border': '1.5px solid #58a70f',
            'borderRadius': '20px',
            'color': 'white',
            'padding': '10px 20px',
            'font-family': 'Inter, sans-serif',
            'font-size': '12px',
            'cursor': 'pointer',
            'marginTop': '10px'
        })
    ], style={
        'backgroundColor': '#34657f',  
        'textAlign': 'center',
        'padding': '0.5em 0',
        'height': '40px',  
        'position': 'fixed',
        'width': '100%',
        'bottom': '0',
        'left': '0',
        'zIndex': '1000',
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center'
    }),
])

server = app.server

@app.callback(
    Output("modal", "is_open"),
    Output("modal-image", "src"),
    Output("stored-click-data", "data"),
    [Input("donut-chart", "clickData"), Input("value-donut-chart", "clickData")],
    [State("modal", "is_open"), State("stored-click-data", "data")]
)
def toggle_modal(click_data_threats, click_data_values, is_open, stored_click_data):
    ctx = callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
        print("Triggered by:", prop_id)
        
        if prop_id in ['donut-chart', 'value-donut-chart'] and (click_data_threats or click_data_values):
            if prop_id == 'donut-chart':
                clicked_data = click_data_threats
            elif prop_id == 'value-donut-chart':
                clicked_data = click_data_values

            clicked_label = clicked_data['points'][0]['label']
            print("Clicked label:", clicked_label)
            image_path = image_mapping.get(clicked_label, '')
            print("Image path:", image_path)
            if image_path:
                return True, image_path, clicked_data

    return is_open, '', stored_click_data

@app.callback(
    [Output('donut-chart', 'clickData'), Output('value-donut-chart', 'clickData')],
    [Input('modal', 'is_open')]
)
def reset_click_data(is_open):
    if not is_open:
        return None, None
    raise PreventUpdate

# Fixed callback with stats updates
@app.callback(
    [Output("map", "figure"),
     Output("donut-chart", "style"),
     Output("value-donut-chart", "style"),
     Output("total-sites", "children"),
     Output("years-monitoring", "children"), 
     Output("avg-threats", "children"),
     Output("avg-values", "children")],
    [Input("map", "clickData"),
     Input('year-slider', 'value')]
)
def update_map_and_stats(click_data, selected_year):
    print("update_map_and_stats function called")
    
    if data.empty:
        # Return empty/default values if no data loaded
        empty_fig = go.Figure()
        return empty_fig, {'display': 'none'}, {'display': 'none'}, "0", "0", "0.0", "0.0"
    
    # Filter the data based on the selected year
    filtered_data = data[data['Year'] == selected_year]
    
    # Calculate stats - only count locations that have valid coordinates (appear on map)
    filtered_map_data = filtered_data.dropna(subset=['Latitude', 'Longitude'])
    total_sites = len(filtered_map_data['Location'].unique()) if not filtered_map_data.empty else 0
    years_range = len(data['Year'].unique())
    avg_threat = filtered_data['Threat Score'].mean() if not filtered_data.empty else 0
    avg_value = filtered_data['Value Score'].mean() if not filtered_data.empty else 0
    
    color_mapping = [
        (lambda x: x < 2.0, 'red'),
        (lambda x: 2.0 <= x < 3.0, 'orange'),
        (lambda x: x >= 3.0, 'green')
    ]

    def get_color_for_value(value):
        for condition, color in color_mapping:
            if condition(value):
                return color
        return 'grey'  # Default color if no condition matches
    
    filtered_data = data[data['Year'] == selected_year].copy()
    if not filtered_data.empty and 'TVR' in filtered_data.columns:
        filtered_data.loc[:, 'Color'] = filtered_data['TVR'].apply(get_color_for_value)
    else:
        filtered_data.loc[:, 'Color'] = 'grey'
        
    # Create a map using Plotly Graph Objects with clustering enabled
    fig = go.Figure(go.Scattermap(
        lat=filtered_data['Latitude'] if not filtered_data.empty else [],
        lon=filtered_data['Longitude'] if not filtered_data.empty else [],
        mode='markers',
        marker=go.scattermap.Marker(
            size=14,
            color=filtered_data['Color'] if not filtered_data.empty else [],
            opacity=0.7
        ),
        text=filtered_data['Location'] if not filtered_data.empty else [],
        hoverinfo='text',
        customdata=filtered_data['Sheet'] if not filtered_data.empty else [],
         hoverlabel=dict(
            bgcolor='#02964a',
            font=dict(
                color='white'
            )
        ),
        cluster=dict(
            enabled=True,
            maxzoom=10,
            step=50,
            color='#0a77a9'
        )
    ))
   
    fig.update_layout(
        map=dict(
            style="open-street-map",
            zoom=zoom_level,
            center=dict(lat=center_lat, lon=center_lon)
        ),
        uirevision='constant',
        height=600
    )
    
    # Show the donut charts when a location is clicked
    if click_data:
        return fig, {'display': 'block'}, {'display': 'block'}, str(total_sites), str(years_range), f"{avg_threat:.1f}", f"{avg_value:.1f}"
    return fig, {'display': 'none'}, {'display': 'none'}, str(total_sites), str(years_range), f"{avg_threat:.1f}", f"{avg_value:.1f}"

@app.callback(
    Output("donut-chart", "figure"),
    [Input("map", "clickData"),
     Input('year-slider', 'value')]
)
def update_donut_chart(click_data, selected_year):
    if not click_data:
        return go.Figure()  # Return an empty figure if no location is clicked

    # Get the clicked location's worksheet from customdata
    worksheet = click_data['points'][0]['customdata']

    # Filter the data for the clicked location's worksheet and selected year
    filtered_data = data[(data['Sheet'] == worksheet) & (data['Year'] == selected_year)]

    # Prepare the data for the donut chart (Threat Type and Threat Score)
    threat_data = filtered_data[['Overall Threat Score', 'Threat Type', 'Threat', 'Threat Score']].groupby(['Overall Threat Score', 'Threat Type', 'Threat']).sum().reset_index()

    # Create a list of labels, parents, and values for the sunburst chart
    overall_threat_labels = threat_data['Overall Threat Score'].unique().tolist()
    threat_labels = threat_data['Threat Type'].unique().tolist()
    data_labels = threat_data['Threat'].tolist()
    data_scores = threat_data['Threat Score'].tolist()

    # Create labels for overall threat score, threat types, and threats
    labels = overall_threat_labels + threat_labels + data_labels

    # Create parents for each level
    overall_threat_parents = [''] * len(overall_threat_labels)
    threat_parents = [threat_data.loc[threat_data['Threat Type'] == threat, 'Overall Threat Score'].iloc[0] for threat in threat_labels]
    data_parents = threat_data['Threat Type'].tolist()

    # Combine all parents
    parents = overall_threat_parents + threat_parents + data_parents

    # Set values for each level
    overall_threat_values = [threat_data.loc[threat_data['Overall Threat Score'] == cat, 'Threat Score'].sum() for cat in overall_threat_labels]
    threat_values = [threat_data.loc[threat_data['Threat Type'] == threat, 'Threat Score'].sum() for threat in threat_labels]
    values = overall_threat_values + threat_values + data_scores

    # Create inside text for each level
    inside_text = [""] + [f"{value:.1f}" for value in threat_values] + [f"{value:.1f}" for value in data_scores ]

    # Create a sunburst chart using Plotly Graph Objects
    fig = go.Figure()

    # Add the sunburst chart (Threat Type and Threat Score)
    fig.add_trace(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,  # Ensure values are correctly set
    branchvalues='total',
    hoverinfo='label',  # Only show the label in the hover information
    text=inside_text,
    name='Threat Type',
    insidetextfont=dict(size=16),  # Set the font size for the inside text
    outsidetextfont=dict(size=30) 
    ))

    
    fig.update_layout(
        title={
            'text': "Threats",
            'y': 0.98,  # Move title to very top
            'x': 0.5,  # Center the title horizontally
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16}  # Smaller title font
        },
        margin=dict(t=30, l=5, r=5, b=5),  # Minimal margins
        height=580,  # Use more of available height
        showlegend=False,  # Remove legend to save space
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)'   # Transparent plot area
    )

    return fig

@app.callback(
    Output('image', 'src'),
    Output('image', 'style'),
    Input('donut-chart', 'clickData')
)
def update_image(click_data):
    if click_data:
        clicked_label = click_data['points'][0]['label']
        print (clicked_label)
        image_path = image_mapping.get(clicked_label, '')
        if image_path:
            return image_path, {'width': '300px', 'height': '300px', 'display': 'block'}
    return '', {'width': '300px', 'height': '300px', 'display': 'none'}
    
@app.callback(
    Output("value-donut-chart", "figure"),
    [Input("map", "clickData"),
     Input('year-slider', 'value')]
)
def update_value_donut_chart(click_data, selected_year):
    if not click_data:
        return go.Figure()  # Return an empty figure if no location is clicked

    # Get the clicked location's worksheet from customdata
    worksheet = click_data['points'][0]['customdata']

    # Filter the data for the clicked location's worksheet and selected year
    filtered_data = data[(data['Sheet'] == worksheet) & (data['Year'] == selected_year)]

    # Prepare the data for the second donut chart (Overall Value Score, Value Type, and Value Score)
    value_data = filtered_data[['Overall Value Score', 'Value Type', 'Value', 'Value Score']].groupby(['Overall Value Score', 'Value Type', 'Value']).sum().reset_index()


    # Create a list of labels, parents, and values for the sunburst chart
    overall_value_labels = value_data['Overall Value Score'].unique().tolist()
    value_type_labels = value_data['Value Type'].unique().tolist()
    value_labels = value_data['Value'].tolist()
    value_scores = value_data['Value Score'].tolist()


    # Create labels for overall value score, value types, and values
    labels = overall_value_labels + value_type_labels + value_labels

    # Create parents for each level
    overall_value_parents = [''] * len(overall_value_labels)
    value_type_parents = [value_data.loc[value_data['Value Type'] == value_type, 'Overall Value Score'].iloc[0] for value_type in value_type_labels]
    value_parents = value_data['Value Type'].tolist()

    # Combine all parents
    parents = overall_value_parents + value_type_parents + value_parents

    # Set values for each level
    overall_value_values = [value_data.loc[value_data['Overall Value Score'] == cat, 'Value Score'].sum() for cat in overall_value_labels]
    value_type_values = [value_data.loc[value_data['Value Type'] == value_type, 'Value Score'].sum() for value_type in value_type_labels]
    values = overall_value_values + value_type_values + value_scores


    # Create inside text for each level
    inside_text =[""] + [f"{value:.1f}" for value in value_type_values] + [f"{value:.1f}" for value in value_scores]
    print("Inside Text:", inside_text)

    # Create a sunburst chart using Plotly Graph Objects
    fig = go.Figure()

    # Add the sunburst chart (Overall Value Score, Value Type, and Value Score)
    fig.add_trace(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,  # Ensure values are correctly set
        branchvalues='total',
        hoverinfo='label',  # Only show the label in the hover information
        text=inside_text,
        name='Value Type',
        insidetextfont=dict(size=16),  # Set the font size for the inside text
        outsidetextfont=dict(size=30)
    ))

    fig.update_layout(
        title={
            'text': "Values",
            'y': 0.98,  # Move title to very top
            'x': 0.5,  # Center the title horizontally
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16}  # Smaller title font
        },
        margin=dict(t=30, l=5, r=5, b=5),  # Minimal margins
        height=580,  # Use more of available height
        showlegend=False,  # Remove legend to save space
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)'   # Transparent plot area
    )
    
    return fig
    
if __name__ == '__main__': 
    app.run_server(debug=False)