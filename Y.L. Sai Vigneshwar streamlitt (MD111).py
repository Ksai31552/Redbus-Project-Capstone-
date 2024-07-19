import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Function to load data from the SQLite database with filters
@st.cache_data
def load_data(query):
    engine = create_engine('sqlite:///buses_data.db')
    df = pd.read_sql(query, con=engine)
    return df

# Streamlit app
st.title("Bus Routes Data")
st.markdown("## Filter and explore bus routes data")

# Sidebar filters
st.sidebar.header("Filters")

# Define initial SQL query
query = "SELECT * FROM bus_routes WHERE 1=1"

# Create a connection to get unique values for dropdowns
engine = create_engine('sqlite:///buses_data.db')
conn = engine.connect()

# Filter by bus type
bus_types_options = pd.read_sql("SELECT DISTINCT [Bus Type] FROM bus_routes", conn)['Bus Type'].tolist()
bus_types = st.sidebar.multiselect(
    "Select Bus Type",
    options=bus_types_options,
    default=bus_types_options  # Default to all options selected
)
if bus_types:
    bus_types_str = ",".join([f"'{bus_type}'" for bus_type in bus_types])
    query += f" AND [Bus Type] IN ({bus_types_str})"

# Filter by route
routes_options = pd.read_sql("SELECT DISTINCT Route FROM bus_routes", conn)['Route'].tolist()
routes = st.sidebar.multiselect(
    "Select Route",
    options=routes_options,
    default=routes_options  # Default to all options selected
)
if routes:
    routes_str = ",".join([f"'{route}'" for route in routes])
    query += f" AND Route IN ({routes_str})"

# Filter by price range
min_price = pd.read_sql("SELECT MIN(CAST(REPLACE(Fare, ',', '') AS FLOAT)) as min_price FROM bus_routes", conn)['min_price'][0]
max_price = pd.read_sql("SELECT MAX(CAST(REPLACE(Fare, ',', '') AS FLOAT)) as max_price FROM bus_routes", conn)['max_price'][0]
selected_min_price, selected_max_price = st.sidebar.slider(
    "Select Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)
query += f" AND CAST(REPLACE(Fare, ',', '') AS FLOAT) BETWEEN {selected_min_price} AND {selected_max_price}"

# Filter by star rating
min_rating = pd.read_sql("SELECT MIN(CAST(COALESCE(NULLIF(Rating, ''), '0') AS FLOAT)) as min_rating FROM bus_routes", conn)['min_rating'][0]
max_rating = pd.read_sql("SELECT MAX(CAST(COALESCE(NULLIF(Rating, ''), '0') AS FLOAT)) as max_rating FROM bus_routes", conn)['max_rating'][0]
selected_min_rating, selected_max_rating = st.sidebar.slider(
    "Select Star Rating Range",
    min_value=min_rating,
    max_value=max_rating,
    value=(min_rating, max_rating)
)
query += f" AND CAST(COALESCE(NULLIF(Rating, ''), '0') AS FLOAT) BETWEEN {selected_min_rating} AND {selected_max_rating}"

# Filter by availability
min_availability = pd.read_sql("SELECT MIN(CAST(COALESCE(NULLIF([Seats Available], ''), '0') AS INT)) as min_availability FROM bus_routes", conn)['min_availability'][0]
max_availability = pd.read_sql("SELECT MAX(CAST(COALESCE(NULLIF([Seats Available], ''), '0') AS INT)) as max_availability FROM bus_routes", conn)['max_availability'][0]
selected_min_availability, selected_max_availability = st.sidebar.slider(
    "Select Seat Availability Range",
    min_value=min_availability,
    max_value=max_availability,
    value=(min_availability, max_availability)
)
query += f" AND CAST(COALESCE(NULLIF([Seats Available], ''), '0') AS INT) BETWEEN {selected_min_availability} AND {selected_max_availability}"

# Close the connection
conn.close()

# Load data with the current filters
df = load_data(query)

# Display data
st.write(f"Total results: {len(df)}")
st.dataframe(df)

# Display summary statistics
st.markdown("## Summary Statistics")
st.write(df.describe())
