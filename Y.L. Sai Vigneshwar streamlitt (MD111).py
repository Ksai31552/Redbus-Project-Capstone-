
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

# Filter by bus type
bus_types = st.sidebar.multiselect(
    "Select Bus Type",
    options=['APSRTC', 'TSRTC', 'KSRTC', 'SBSTC', 'WBTC', 'HRTC', 'RSRTC', 'ASTC'],
    default=[]
)
if bus_types:
    bus_types_str = ",".join([f"'{bus_type}'" for bus_type in bus_types])
    query += f" AND [Bus Type] IN ({bus_types_str})"

# Filter by route
routes = st.sidebar.multiselect(
    "Select Route",
    options=[],
    default=[]
)
if routes:
    routes_str = ",".join([f"'{route}'" for route in routes])
    query += f" AND Route IN ({routes_str})"

# Filter by price range
min_price, max_price = st.sidebar.slider(
    "Select Price Range",
    min_value=0,
    max_value=10000,
    value=(0, 10000)
)
query += f" AND CAST(REPLACE(Fare, ',', '') AS FLOAT) BETWEEN {min_price} AND {max_price}"

# Filter by star rating
min_rating, max_rating = st.sidebar.slider(
    "Select Star Rating Range",
    min_value=0.0,
    max_value=5.0,
    value=(0.0, 5.0)
)
query += f" AND CAST(COALESCE(NULLIF(Rating, ''), '0') AS FLOAT) BETWEEN {min_rating} AND {max_rating}"

# Filter by availability
min_availability, max_availability = st.sidebar.slider(
    "Select Seat Availability Range",
    min_value=0,
    max_value=100,
    value=(0, 100)
)
query += f" AND CAST(COALESCE(NULLIF([Seats Available], ''), '0') AS INT) BETWEEN {min_availability} AND {max_availability}"

# Load data with the current filters
df = load_data(query)

# Display data
st.write(f"Total results: {len(df)}")
st.dataframe(df)

# Display summary statistics
st.markdown("## Summary Statistics")
st.write(df.describe())

# To run the app, use the command: Step 1 (in annaconda prompt):   cd C:\Users\Sai.Vigneshwar\Desktop
#Step 2: streamlit run demo.py

##########################################################
#this code is to cross check that the file exist or not

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('buses_data.db')

# Create a cursor object
cursor = conn.cursor()

# Query to check if the table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bus_routes';")

# Fetch the result
table_exists = cursor.fetchone()

if table_exists:
    print("Table 'bus_routes' exists.")
else:
    print("Table 'bus_routes' does not exist.")

# Close the connection
conn.close()





