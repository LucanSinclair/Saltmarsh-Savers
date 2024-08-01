import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo

# Read data from Excel for Threats
df_threats = pd.read_excel(r"C:\Users\LucanSinclair\OneDrive - Earthwatch\Desktop\Test\test.xlsx", sheet_name='Threats')

# Read data from Excel for Values
df_values = pd.read_excel(r"C:\Users\LucanSinclair\OneDrive - Earthwatch\Desktop\Test\test.xlsx", sheet_name='Values')

# Threats Chart
inner_labels = df_threats['Category'].dropna().tolist()
inner_values = df_threats['Value'].dropna().tolist()
outer_labels = df_threats['Subcategory'].dropna().tolist()
outer_values = df_threats['Subvalue'].dropna().tolist()

inner_colors = ['#FF9999', '#9999FF']  # Red for 'H', Blue for 'C'
outer_colors = [
    '#FFCCCC', '#FFB3B3', '#FF9999', '#FF8080', '#FF6666', '#FF4D4D', '#FF3333', '#FF1A1A', '#FF0000', '#E60000', 
    '#CC0000', '#B30000', '#990000', '#800000', '#660000', '#4D0000',  # Shades of red for human influences
    '#CCCCFF', '#B3B3FF', '#9999FF', '#8080FF', '#6666FF', '#4D4DFF', '#3333FF', '#1A1AFF', '#0000FF', '#0000E6', 
    '#0000CC', '#0000B3', '#000099', '#000080', '#000066', '#00004D'   # Shades of blue for climate influences
]

data_threats = [
    go.Pie(
        values=inner_values,
        labels=inner_labels,
        domain={'x': [0.2, 0.8], 'y': [0.1, 0.9]},
        hole=0.5,
        direction='clockwise',
        sort=False,
        marker={'colors': inner_colors}
    ),
    go.Pie(
        values=outer_values,
        labels=outer_labels,
        domain={'x': [0.1, 0.9], 'y': [0, 1]},
        hole=0.75,
        direction='clockwise',
        sort=False,
        marker={'colors': outer_colors},
        showlegend=False
    )
]

layout_threats = go.Layout(
    title='Threats',
    legend=dict(
        x=1.1,  # Position the legend outside the plot area
        y=0.5,
        traceorder='normal',
        font=dict(size=10),
        bgcolor='rgba(0,0,0,0)'
    ),
  margin=dict(l=50, r=150, t=50, b=50),  # Increase right margin to accommodate the legend
    annotations=[
        dict(
            text='37.85',  # Text to display in the center
            x=0.5, y=0.5,  # Position in the center
            font_size=26,
            showarrow=False
        )
    ]
)

fig_threats = go.Figure(data=data_threats, layout=layout_threats)
pyo.plot(fig_threats, filename='threats_chart.html')

# Values Chart
values_labels = df_values['Category'].dropna().tolist()
values_values = df_values['Value'].dropna().tolist()

# Define sequential shades of green
values_colors = [
    '#E6F2E6', '#CCE5CC', '#B3D8B3', '#99CC99', '#80BF80', '#66B266', '#4DA64D', '#339933', '#1A8C1A', '#008000',
    '#007300', '#006600', '#005900', '#004C00', '#003F00', '#003300', '#002600', '#001900', '#001300', '#000D00',
    '#000C00', '#000000'
]

data_values = [
    go.Pie(
        values=values_values,
        labels=values_labels,
        domain={'x': [0, 1], 'y': [0, 1]},  # Use the full domain for the pie chart
        hole=0.5,
        direction='clockwise',
        sort=False,
        marker={'colors': values_colors}
    )
]

layout_values = go.Layout(
    title='Values',
    legend=dict(
        x=1.1,  # Position the legend outside the plot area
        y=0.5,
        traceorder='normal',
        font=dict(size=10),
        bgcolor='rgba(0,0,0,0)'
    ),
    margin=dict(l=50, r=150, t=50, b=50),  # Increase right margin to accommodate the legend
    annotations=[
        dict(
            text='64.54',  # Text to display in the center
            x=0.5, y=0.5,  # Position in the center
            font_size=26,
            showarrow=False
        )
    ]
)

fig_values = go.Figure(data=data_values, layout=layout_values)
pyo.plot(fig_values, filename='values_chart.html')