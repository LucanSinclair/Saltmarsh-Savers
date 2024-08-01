import pandas as pd
import plotly.graph_objs as go
import plotly.offline as pyo

# Read data from Excel for Threats
df_threats = pd.read_excel(r"C:\Users\LucanSinclair\OneDrive - Earthwatch\Desktop\Code\Earthwatch_Code\Saltmarsh-Savers\test.xlsx", sheet_name='Threats')

# Read data from Excel for Values
df_values = pd.read_excel(r"C:\Users\LucanSinclair\OneDrive - Earthwatch\Desktop\Code\Earthwatch_Code\Saltmarsh-Savers\test.xlsx", sheet_name='Values')

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
        marker={'colors': inner_colors},
        hovertemplate='%{label}: %{value:.1f}%<extra></extra>',  # Limit decimal places to 1  
         texttemplate='%{label}',
         showlegend=False
        ),

    go.Pie(
        values=outer_values,
        labels=outer_labels,
        domain={'x': [0.1, 0.9], 'y': [0, 1]},
        hole=0.75,
        direction='clockwise',
        sort=False,
        marker={'colors': outer_colors},
        hovertemplate='%{label}: %{value:.1f}%<extra></extra>',  # Limit decimal places to 1
        texttemplate='%{value:.1f}%',  # Limit decimal places to 1 in labels
        
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
inner_labels_values = df_values['Category'].dropna().tolist()
inner_values_values = df_values['Value'].dropna().tolist()
outer_labels_values = df_values['Subcategory'].dropna().tolist()
outer_values_values = df_values['Subvalue'].dropna().tolist()

# Define colors for 6 categories and 22 subcategories
inner_colors_values = [ '#5cbfe6', '#10968f', '#fdca5a', '#89bb4d', '#ef8165', '#f15740']  # Different shades of green for categories
outer_colors_values = [
    '#E6F2E6', '#CCE5CC', '#B3D8B3', '#99CC99', '#80BF80', '#66B266', '#4DA64D', '#339933', '#1A8C1A', '#008000',
'#007A00', '#007300', '#006D00', '#006600', '#006000', '#005900', '#005300', '#004C00', '#004600', '#004000',
'#003A00', '#003300'
]

data_values = [
    go.Pie(
        values=inner_values_values,
        labels=inner_labels_values,
        domain={'x': [0.2, 0.8], 'y': [0.1, 0.9]},
        hole=0.5,
        direction='clockwise',
        sort=False,
        marker={'colors': inner_colors_values},
        hovertemplate='%{label}: %{value:.1f}%<extra></extra>',  # Limit decimal places to 1 
        texttemplate='%{label}',
        showlegend=False
        ),

    go.Pie(
        values=outer_values_values,
        labels=outer_labels_values,
        domain={'x': [0.1, 0.9], 'y': [0, 1]},
        hole=0.75,
        direction='clockwise',
        sort=False,
        marker={'colors': outer_colors_values},
        hovertemplate='%{label}: %{value:.1f}%<extra></extra>',  # Limit decimal places to 1
        texttemplate='%{value:.1f}%',
        
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