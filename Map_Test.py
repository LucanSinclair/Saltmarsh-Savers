import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dash import Dash, dcc, html, Input, Output

# Define the path to the directory containing the Excel files
data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Load the Excel data from multiple files and add a column to identify the year
years = [2023, 2024]  # Add more years as needed
data_frames = []
for year in years:
    file_path = os.path.join(data_dir, f'data_{year}.xlsx')
    sheet_names = pd.ExcelFile(file_path).sheet_names
    for sheet in sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet).assign(Year=year, Sheet=sheet)
        data_frames.append(df)
data = pd.concat(data_frames, ignore_index=True)
print(f"Data Loaded:\n{data.head()}")

# Calculate the bounding box of the data points
min_lat = data['Latitude'].min()
max_lat = data['Latitude'].max()
min_lon = data['Longitude'].min()
max_lon = data['Longitude'].max()

# Calculate the center of the map based on the bounding box
center_lat = (min_lat + max_lat) / 2
center_lon = (min_lon + max_lon) / 2

# Calculate the zoom level based on the bounding box
def calculate_zoom(min_lat, max_lat, min_lon, max_lon):
    lat_diff = max_lat - min_lat
    lon_diff = max_lon - min_lon
    max_diff = max(lat_diff, lon_diff)
    zoom = 8 - (max_diff * 10)  # Adjust the multiplier as needed
    return max(1, min(zoom, 15))  # Ensure zoom level is within a reasonable range

zoom_level = calculate_zoom(min_lat, max_lat, min_lon, max_lon)

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.Header([
        html.Div([
            html.H1("Saltmarsh Savers", style={
                'color': 'white',
                'font-family': 'Arial, sans-serif',
                'font-size': '24px',
                'margin': '0'  # Remove default margin
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
        'backgroundColor': '#253746',  # Solid color
        'textAlign': 'center',
        'padding': '1em 0',
        'height': '80px',
        'position': 'fixed',
        'width': '100%',
        'top': '0',
        'left': '0',
        'zIndex': '1000',  # Ensure the header is on top
    }),
    html.Div([
        html.Div([
            dcc.Graph(id='map', style={'width': '100%', 'height': '100%', 'margin': '0', 'padding': '0'}),
        ], style={'width': '50%', 'height': '500px', 'minHeight': '500px', 'margin': 'auto'}),
        html.Div([
            dcc.Graph(id='donut-chart', style={'width': '100%', 'height': '100%', 'margin': '0', 'padding': '0'}),
        ], style={'width': '25%', 'height': '500px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center', 'flexShrink': '0'}),
        html.Div([
            dcc.Graph(id='value-donut-chart', style={'width': '100%', 'height': '100%', 'margin': '0', 'padding': '0'})
        ], style={'width': '25%', 'height': '500px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center', 'flexShrink': '0'})
    ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', 'marginTop': '80px', 'height': '500px', 'flexShrink': '0', 'marginBottom': '25px'}),
    html.Div([
        dcc.Slider(
            id='year-slider',
            min=min(years),
            max=max(years),
            value=max(years),
            marks={str(year): {'label': str(year), 'style': {'font-size': '14px', 'font-family': 'Arial, sans-serif'}} for year in years},
            step=None
        )
    ], style={'width': '50%', 'margin': 'auto'}),
    html.Footer([
        html.P("", style={
            'color': 'white',
            'font-family': 'Arial, sans-serif',
            'font-size': '12px',
            'margin': '0'  # Remove default margin
        }),
        html.Button("Contact us", style={
            'backgroundColor': 'transparent',
            'border': '1.5px solid #58a70f',
            'borderRadius': '20px',  # Make the button oval
            'color': 'white',
            'padding': '10px 20px',
            'font-family': 'Arial, sans-serif',
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
    })
])

print("Layout defined")
server = app.server

@app.callback(
    [Output("map", "figure"),
     Output("donut-chart", "style"),
     Output("value-donut-chart", "style")],
    [Input("map", "clickData"),
     Input('year-slider', 'value')]
)
def update_map(click_data, selected_year):
    print("update_map function called")
    # Filter the data based on the selected year
    filtered_data = data[data['Year'] == selected_year]
    
    print(f"Selected Year: {selected_year}")
    print(f"Filtered Data:\n{filtered_data.head()}")

    color_mapping = [
        (lambda x: x < 2.0, 'green'),
        (lambda x: 2.0 <= x < 3.0, 'orange'),
        (lambda x: x >= 3.0, 'red')
    ]

    def get_color_for_value(value):
        for condition, color in color_mapping:
            if condition(value):
                return color
        return 'grey'  # Default color if no condition matches
    
    filtered_data['Color'] = filtered_data['TVR'].apply(get_color_for_value)

    # Create a map using Plotly Graph Objects with clustering enabled
    fig = go.Figure(go.Scattermapbox(
        lat=filtered_data['Latitude'],
        lon=filtered_data['Longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14,
            color=filtered_data['Color'],
            opacity=0.7
        ),
        text=filtered_data['Location'],
        hoverinfo='text',
        customdata=filtered_data['Sheet'],  # Add custom data for each point
         hoverlabel=dict(
            bgcolor='#02964a',  # Set the background color of the hover text
            font=dict(
                color='white'  # Set the color of the hover text
            )
        ),
        cluster=dict(
            enabled=True,
            maxzoom=10,
            step=50,
            color='#0a77a9'  # Set the color of the cluster dots
        )
    ))
   
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            zoom=zoom_level,
            center=dict(lat=center_lat, lon=center_lon)  # Center the map based on data points
        ),
        uirevision='constant',
        height=600
    )
    
    # Show the donut charts when a location is clicked
    if click_data:
        return fig, {'display': 'block'}, {'display': 'block'}
    return fig, {'display': 'none'}, {'display': 'none'}

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
    threat_parents = [threat_data.loc[threat_data['Threat Type'] == threat, 'Overall Threat Score'].values[0] for threat in threat_labels]
    data_parents = threat_data['Threat Type'].tolist()

    # Combine all parents
    parents = overall_threat_parents + threat_parents + data_parents

    # Set values for each level
    overall_threat_values = [threat_data[threat_data['Overall Threat Score'] == cat]['Threat Score'].sum() for cat in overall_threat_labels]
    threat_values = [threat_data[threat_data['Threat Type'] == threat]['Threat Score'].sum() for threat in threat_labels]
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
            'y': 0.82,  # Adjust this value to move the title closer to the donut graph
            'x': 0.5,  # Center the title horizontally
            'xanchor': 'center',
            'yanchor': 'top'
        },
        margin=dict(t=30, l=10, r=10, b=10)  # Adjust margins if needed
    )

    return fig

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
    value_type_parents = [value_data.loc[value_data['Value Type'] == value_type, 'Overall Value Score'].values[0] for value_type in value_type_labels]
    value_parents = value_data['Value Type'].tolist()

    # Combine all parents
    parents = overall_value_parents + value_type_parents + value_parents

    # Set values for each level
    overall_value_values = [value_data[value_data['Overall Value Score'] == cat]['Value Score'].sum() for cat in overall_value_labels]
    value_type_values = [value_data[value_data['Value Type'] == value_type]['Value Score'].sum() for value_type in value_type_labels]
    values = overall_value_values + value_type_values + value_scores

    # Create inside text for each level
    inside_text =[""] + [f"{value:.1f}" for value in overall_value_values] + [f"{value:.1f}" for value in value_type_values] + [f"{value:.1f}" for value in value_scores]

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
            'y': 0.82,  # Adjust this value to move the title closer to the donut graph
            'x': 0.5,  # Center the title horizontally
            'xanchor': 'center',
            'yanchor': 'top'
        },
        margin=dict(t=30, l=10, r=10, b=0),  # Adjust margins if needed
    )
    
    return fig
    
if __name__ == '__main__': 
    app.run_server(debug=False)