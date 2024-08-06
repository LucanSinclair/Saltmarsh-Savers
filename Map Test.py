import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash import Dash, dcc, html, Input, Output

# Define the path to the Excel file
file_path = r'C:\Users\LucanSinclair\OneDrive - Earthwatch\Desktop\data.xlsx'  # Use raw string to avoid escape character issues

# Load the Excel data from multiple sheets and add a column to identify the worksheet
sheet_names = pd.ExcelFile(file_path).sheet_names
data_frames = [pd.read_excel(file_path, sheet_name=sheet).assign(Sheet=sheet) for sheet in sheet_names]
data = pd.concat(data_frames, ignore_index=True)

# Initialize the Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Graph(id='map'),  # Add a component with the ID "map"
    ], style={'width': '50%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='donut-chart', style={'display': 'none'}),  # Initially hidden
        dcc.Graph(id='value-donut-chart', style={'display': 'none'})  # Initially hidden
    ], style={'width': '50%', 'display': 'inline-block'}),
])

@app.callback(
    [Output("map", "figure"),
     Output("donut-chart", "style"),
     Output("value-donut-chart", "style")],
    Input("map", "clickData")
)
def update_map(click_data):
    # Create a map using Plotly Express
    fig = px.scatter_mapbox(
        data,
        lat="Latitude",  # Ensure this is the correct column name for latitude
        lon="Longitude",  # Ensure this is the correct column name for longitude
        hover_name="Location",  # Ensure this is the correct column name for hover information
        zoom=3,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    
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

    # Get the clicked location's worksheet
    location = click_data['points'][0]['hovertext']
    worksheet = data.loc[data['Location'] == location, 'Sheet'].values[0]

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
        title_text="Threats"
    )

    return fig

@app.callback(
    Output("value-donut-chart", "figure"),
    Input("map", "clickData")
)
def update_value_donut_chart(click_data):
    if not click_data:
        return go.Figure()  # Return an empty figure if no location is clicked

    # Get the clicked location's worksheet
    location = click_data['points'][0]['hovertext']
    worksheet = data.loc[data['Location'] == location, 'Sheet'].values[0]

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
        title_text="Values"
    )
    
    return fig
    
if __name__ == '__main__':
    app.run_server(debug=True)