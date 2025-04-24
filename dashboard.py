import pandas as pd
import plotly.express as px
import requests
from dash import Dash, html, dcc, Input, Output, callback
import dash

# Initialize the app
app = Dash(__name__)

# API configuration
API_BASE_URL = "http://localhost:5000"

def fetch_data():
    """Fetch data from the Flask API with error handling"""
    try:
        response = requests.get(f"{API_BASE_URL}/annonces", timeout=10)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def preprocess_data(df):
    """Clean and prepare the data for visualization"""
    if df.empty:
        return df
    
    # Convert price (FIXED: Proper regex escape sequence)
    if 'price' in df.columns:
        df['price'] = (
            df['price']
            .astype(str)
            .str.replace(r'[^\d]', '', regex=True)  # Fixed escape sequence
            .pipe(pd.to_numeric, errors='coerce')
        )
    
    # Convert dates (DD/MM/YYYY format)
    if 'publication_date' in df.columns:
        df['publication_date'] = pd.to_datetime(
            df['publication_date'],
            dayfirst=True,
            errors='coerce'
        )
    
    # Remove extreme outliers (top 1%)
    if 'price' in df.columns:
        df = df[df['price'] <= df['price'].quantile(0.99)]
    
    return df

# Initial data load
df = preprocess_data(fetch_data())

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Tunisie Annonce Dashboard", 
               style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.P("Interactive real estate analytics", 
              style={'textAlign': 'center', 'color': '#7f8c8d'})
    ], style={'marginBottom': '20px'}),
    
    # Filters and Refresh
    html.Div([
        html.Div([
            html.Label("Location:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='location-filter',
                options=[{'label': 'All Locations', 'value': 'all'}] + 
                        [{'label': loc, 'value': loc} for loc in df['location'].unique()],
                value='all',
                clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label("Property Type:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='property-type-filter',
                options=[{'label': 'All Types', 'value': 'all'}] + 
                        [{'label': typ, 'value': typ} for typ in df['property_type'].unique()],
                value='all',
                clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Br(),
            html.Button("🔄 Refresh Data", id='refresh-button', 
                      style={'background-color': '#3498db', 'color': 'white', 'border': 'none'})
        ], style={'width': '20%', 'display': 'inline-block', 'textAlign': 'center'})
    ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px', 'marginBottom': '20px'}),
    
    # Summary Statistics Cards (RETURNED AS REQUESTED)
    html.Div([
        html.Div([
            html.Div([
                html.H4("Total Listings", style={'color': '#3498db', 'marginBottom': '5px'}),
                html.H2(id='total-listings', style={'color': '#2c3e50', 'marginTop': '0'})
            ], className='card', style={'padding': '15px', 'textAlign': 'center'})
        ], style={'width': '24%', 'display': 'inline-block'}),
        
        html.Div([
            html.Div([
                html.H4("Average Price", style={'color': '#3498db', 'marginBottom': '5px'}),
                html.H2(id='avg-price', style={'color': '#2c3e50', 'marginTop': '0'})
            ], className='card', style={'padding': '15px', 'textAlign': 'center'})
        ], style={'width': '24%', 'display': 'inline-block'}),
        
        html.Div([
            html.Div([
                html.H4("Most Common Type", style={'color': '#3498db', 'marginBottom': '5px'}),
                html.H2(id='common-type', style={'color': '#2c3e50', 'marginTop': '0'})
            ], className='card', style={'padding': '15px', 'textAlign': 'center'})
        ], style={'width': '24%', 'display': 'inline-block'}),
        
        html.Div([
            html.Div([
                html.H4("Top Location", style={'color': '#3498db', 'marginBottom': '5px'}),
                html.H2(id='top-location', style={'color': '#2c3e50', 'marginTop': '0'})
            ], className='card', style={'padding': '15px', 'textAlign': 'center'})
        ], style={'width': '24%', 'display': 'inline-block'})
    ], style={'marginBottom': '20px'}),
    
    # Main Visualizations
    html.Div([
        html.Div([
            dcc.Graph(id='price-distribution')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(id='property-type-distribution')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right', 'padding': '10px'})
    ]),
    
    # Bottom Visualizations
    html.Div([
        html.Div([
            dcc.Graph(id='price-by-location')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(id='property-types-by-location')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right', 'padding': '10px'})
    ]),
    
    # Hidden storage
    dcc.Store(id='data-store', data=df.to_dict('records'))
], style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'})

# Callbacks
@callback(
    Output('data-store', 'data'),
    Input('refresh-button', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    new_data = fetch_data()
    return preprocess_data(new_data).to_dict('records')

@callback(
    Output('total-listings', 'children'),
    Output('avg-price', 'children'),
    Output('common-type', 'children'),
    Output('top-location', 'children'),
    Output('price-distribution', 'figure'),
    Output('property-type-distribution', 'figure'),
    Output('price-by-location', 'figure'),
    Output('property-types-by-location', 'figure'),
    Input('data-store', 'data'),
    Input('location-filter', 'value'),
    Input('property-type-filter', 'value')
)
def update_dashboard(data, location, property_type):
    df = pd.DataFrame(data)
    
    # Apply filters
    if location != 'all' and 'location' in df.columns:
        df = df[df['location'] == location]
    if property_type != 'all' and 'property_type' in df.columns:
        df = df[df['property_type'] == property_type]
    
    # Calculate summary stats (RETURNED AS REQUESTED)
    stats = {
        'total': len(df),
        'avg_price': f"{df['price'].mean():,.0f} DT" if 'price' in df.columns and not df.empty else "N/A",
        'common_type': df['property_type'].mode()[0] if 'property_type' in df.columns and not df.empty else "N/A",
        'top_location': df['location'].mode()[0] if 'location' in df.columns and not df.empty else "N/A"
    }
    
    # 1. Price Distribution
    price_fig = px.histogram(
        df, x='price', nbins=30,
        title=f'Price Distribution ({stats["total"]} listings)',
        color_discrete_sequence=['#3498db']
    ).update_layout(yaxis_title="Number of Listings")
    
    # 2. Property Type Distribution
    type_fig = px.pie(
        df, names='property_type', 
        title=f'Property Types ({stats["common_type"]} most common)',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # 3. Price by Location (Box Plot)
    if 'location' in df.columns and not df.empty:
        top_locations = df['location'].value_counts().nlargest(10).index
        filtered_df = df[df['location'].isin(top_locations)]
        price_loc_fig = px.box(
            filtered_df, x='location', y='price',
            title='Price Distribution by Location (Top 10)',
            color='location'
        ).update_layout(
            xaxis_title="",
            yaxis_title="Price (DT)",
            showlegend=False
        )
    else:
        price_loc_fig = px.scatter(title="No location data available")
    
    # 4. Property Types by Location
    if all(col in df.columns for col in ['location', 'property_type']) and not df.empty:
        type_loc_df = df.groupby(['location', 'property_type']).size().reset_index(name='count')
        top_locs = df['location'].value_counts().nlargest(8).index
        type_loc_df = type_loc_df[type_loc_df['location'].isin(top_locs)]
        type_loc_fig = px.bar(
            type_loc_df, x='location', y='count', color='property_type',
            title='Property Types by Location (Top 8)',
            barmode='stack'
        ).update_layout(
            xaxis_title="",
            yaxis_title="Number of Listings"
        )
    else:
        type_loc_fig = px.scatter(title="No location/property type data available")
    
    return (
        stats['total'],
        stats['avg_price'],
        stats['common_type'],
        stats['top_location'],
        price_fig,
        type_fig,
        price_loc_fig,
        type_loc_fig
    )

if __name__ == '__main__':
    app.run(debug=True)