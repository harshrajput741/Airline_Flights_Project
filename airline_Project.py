import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set the title of the app
st.set_page_config(page_title="Airline Dashboard", layout="wide")
st.title("Airline Executive Insights Dashboard")

df = pd.read_csv("cleaned_airline_dataset.csv")
st.dataframe(df)

df['Total_Stops'] = df['total_stops'].replace({'non-stop':0,'1 stop':1,'2 stop':2, '3 stop':3, '4 stop':4}) 

st.sidebar.header("Filter")

airlines = ['All Airlines'] + list(df['airline'].unique())
selected_airline = st.sidebar.multiselect("Select Airline", airlines)

selected_source = st.sidebar.selectbox("Select Source",df['source_city'].unique())
selected_destination = st.sidebar.selectbox("Select Destination",df['destination_city'].unique())

filtered_df = df.copy()
if not selected_airline:
    st.warning("Please select at least one airline.")
    st.stop()

### Condition 2: All Airline is selected
elif 'All Airlines' in selected_airline:
    filtered_df = df.copy()
    st.write("Total Airlines: ", filtered_df.shape[0])
    st.dataframe(df)

### Condition 3: Specific Airlines are selected
else:
    filtered_df = df[df['Airline'].isin(selected_airline)]
    st.write(f"{selected_airline} Airlines",filtered_df.shape[0])
    st.dataframe(filtered_df)

### KPI Section for Selected Airlines
st.subheader("Key Metrics for Selected Airlines" f"{selected_airline}")
col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df['price'].sum()
avg_price = filtered_df['price'].mean()
max_price = filtered_df['price'].max()
min_price = filtered_df['price'].min()



col1.metric("Total Revenue",f"{int(total_revenue): ,}")
col2.metric("Minimum Price",f"{int(min_price): ,}")
col3.metric("Average Price",f"{int(avg_price): ,}")
col4.metric("Maximum Price",f"{int(max_price): ,}")



### Filtering Source
if selected_source:
    filtered_df = filtered_df[filtered_df['source_city'] == selected_source] # applying filter from selected airline to selected selected_destination
    filtered_destination = [df['source_city']] == selected_source

### Filtering Destination
if selected_destination:
    filtered_df = filtered_df[filtered_df['destination_city'] == selected_destination] # applying filter from selected airline to selected selected_destination
    filtered_destination = [df['destination_city']] == selected_destination


### KPI Section for source to Destination
st.subheader('Key Metrics for Selected Source' f"{selected_source} To Destination {selected_destination}")
col, col2, col3, col4 = st.columns(4)

#total_revenue = 


### Condition 1


### Condition 2