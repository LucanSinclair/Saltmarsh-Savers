import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dash import Dash, dcc, html, Input, Output

# Define the path to the Excel file
file_path = os.path.join(os.path.dirname(__file__), 'data.xlsx')

# Load the Excel data from multiple sheets and add a column to identify the worksheet
sheet_names = pd.ExcelFile(file_path).sheet_names
data_frames = [pd.read_excel(file_path, sheet_name=sheet).assign(Sheet=sheet) for sheet in sheet_names]
data = pd.concat(data_frames, ignore_index=True)

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
    ], style={'width': '50%', 'height': '500px', 'minHeight': '500px'}),
    html.Div([
        dcc.Graph(id='donut-chart', style={'width': '100%', 'height': '100%', 'margin': '0', 'padding': '0'}),
    ], style={'width': '25%', 'height': '500px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center', 'flexShrink': '0'}),
    html.Div([
        dcc.Graph(id='value-donut-chart', style={'width': '100%', 'height': '100%', 'margin': '0', 'padding': '0'})
    ], style={'width': '25%', 'height': '500px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center', 'flexShrink': '0'})
], style={'display': 'flex', 'marginTop': '80px', 'height': '500px', 'flexShrink': '0'}),
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

@app.callback(
    [Output("map", "figure"),
     Output("donut-chart", "style"),
     Output("value-donut-chart", "style")],
    Input("map", "clickData")
)
def update_map(click_data):
    # Create a map using Plotly Graph Objects with clustering enabled
    fig = go.Figure(go.Scattermapbox(
        lat=data['Latitude'],
        lon=data['Longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14,
            color='#0a77a9',
            opacity=0.7
        ),
        text=data['Location'],
        hoverinfo='text',
        customdata=data['Sheet'],  # Add custom data for each point
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
    Input("map", "clickData")
)
def update_donut_chart(click_data):
    if not click_data:
        return go.Figure()  # Return an empty figure if no location is clicked

    # Get the clicked location's worksheet from customdata
    worksheet = click_data['points'][0]['customdata']

    # Filter the data for the clicked location's worksheet
    filtered_data = data[data['Sheet'] == worksheet]

    # Prepare the data for the donut chart (Threat Type and Threat Score)
    threat_data = filtered_data[['Threat Type', 'Threat Score']].groupby('Threat Type').sum().reset_index()

    # Create a list of labels, parents, and values for the sunburst chart
    threat_labels = threat_data['Threat Type'].tolist()
    data_labels = filtered_data['Threat'].tolist()
    data_scores = filtered_data['Threat Score'].tolist()

    labels = threat_labels + [f"{label} ({value:.1f})" for label, value in zip(data_labels, data_scores)]
    parents = [''] * len(threat_labels) + filtered_data['Threat Type'].tolist()
    inside_text = [f"{value:.1f}" for value in threat_data['Threat Score']] + [f"{value:.1f}" for value in data_scores]

    # Create a sunburst chart using Plotly Graph Objects
    fig = go.Figure()

    # Add the sunburst chart (Threat Type and Threat Score)
    fig.add_trace(go.Sunburst(
        labels=labels,
        parents=parents,
        values=threat_data['Threat Score'].tolist() + data_scores,  # Ensure values are correctly set
        branchvalues='total',
        hoverinfo='label',  # Only show the label in the hover information
        text=inside_text,
        name='Threat Type'
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
    Input("map", "clickData")
)
def update_value_donut_chart(click_data):
    if not click_data:
        return go.Figure()  # Return an empty figure if no location is clicked

    # Get the clicked location's worksheet from customdata
    worksheet = click_data['points'][0]['customdata']

    # Filter the data for the clicked location's worksheet
    filtered_data = data[data['Sheet'] == worksheet]

    # Prepare the data for the second donut chart (Value Type and Value Score)
    value_data = filtered_data[['Value Type', 'Value Score']].groupby('Value Type').sum().reset_index()

    # Create a list of labels, parents, and values for the sunburst chart
    value_labels = value_data['Value Type'].tolist()
    value_data_labels = filtered_data['Value'].tolist()
    value_data_scores = filtered_data['Value Score'].tolist()

    labels = value_labels + [f"{label} ({value:.1f})" for label, value in zip(value_data_labels, value_data_scores)]
    parents = [''] * len(value_labels) + filtered_data['Value Type'].tolist()
    inside_text = [f"{value:.1f}" for value in value_data['Value Score']] + [f"{value:.1f}" for value in value_data_scores]

    # Create a sunburst chart using Plotly Graph Objects
    fig = go.Figure()

    # Add the sunburst chart (Value Type and Value Score)
    fig.add_trace(go.Sunburst(
        labels=labels,
        parents=parents,
        values=value_data['Value Score'].tolist() + value_data_scores,  # Ensure values are correctly set
        branchvalues='total',
        hoverinfo='label',  # Only show the label in the hover information
        text=inside_text,
        name='Value Type'
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
    #annotations=[
        #dict(
            #x=0.5,  # X position of the annotation
            #y=0.5,  # Y position of the annotation
            #text="6",  # Custom text to display
            #showarrow=False,
            #font=dict(size=40, color="white"),
            #xanchor='center',
            #yanchor='middle'
        #)
    #],
)
    
    return fig
    
if __name__ == '__main__':
    app.run_server(debug=False)