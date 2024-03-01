import pandas as pd
import streamlit as st
import locale
from datetime import datetime, timedelta

# Set the locale for formatting currency (USD)
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Read the CSV file into a pandas DataFrame
file_path = r"C:\Users\gu055805\OneDrive - intelbras.com.br\Documentos\pythonProject\Microchip backlog.csv"
try:
    df = pd.read_csv(file_path, sep=';')
except Exception as e:
    st.error(f"Error reading CSV file: {e}")
    st.stop()

# Replace commas with periods in the Price column
df['Price'] = df['Price'].str.replace(',', '.')

# Convert the ship date column to datetime format
try:
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%d/%m/%Y')
except Exception as e:
    st.error(f"Error converting Ship Date column: {e}")
    st.stop()

# Filter by Date Range
date_range = st.sidebar.date_input("Select Date Range", [df['Ship Date'].min(), df['Ship Date'].max()])
start_date, end_date = date_range

# Convert start_date and end_date to Timestamp objects
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

filtered_df = df[(df['Ship Date'] >= start_date) & (df['Ship Date'] <= end_date)]

# Filter by Mode
selected_modes = st.sidebar.multiselect("Select Modes", df['Mode'].unique(), default=df['Mode'].unique())

# Apply Mode filter
filtered_df = filtered_df[filtered_df['Mode'].isin(selected_modes)]

# Resample data by month and count unique AWBs
monthly_unique_awbs = filtered_df.resample('MS', on='Ship Date')['Waybill Nbr - Ship Warehouse'].nunique()

# Function to calculate cost savings
def calculate_cost_savings(df):
    # Calculate the number of weeks in the specified date range
    num_weeks = (end_date - start_date).days // 7

    # Calculate actual spending: number of unique AWBs * cost per AWB
    actual_spending = df['Waybill Nbr - Ship Warehouse'].nunique() * 200

    # Calculate consolidated operation: number of weeks * cost per AWB
    consolidated_operation = num_weeks * 200

    return actual_spending, consolidated_operation, num_weeks

# Calculate actual spending, consolidated operation, and number of weeks for filtered data
actual_spending, consolidated_operation, num_weeks = calculate_cost_savings(filtered_df)

# Calculate repeated AWBs
repeated_awbs = len(filtered_df) - len(filtered_df['Waybill Nbr - Ship Warehouse'].unique())

# Calculate number of unique AWBs for the entire dataset
unique_awbs_total = df['Waybill Nbr - Ship Warehouse'].nunique()

# Calculate projected savings
projected_savings = actual_spending - consolidated_operation

# Format the amounts into dollar currency
actual_spending_formatted = locale.currency(actual_spending, grouping=True)
consolidated_operation_formatted = locale.currency(consolidated_operation, grouping=True)
projected_savings_formatted = locale.currency(projected_savings, grouping=True)

# Create a DataFrame for the comparison
comparison_df = pd.DataFrame({
    'Type': ['Actual Spending', 'Consolidated Operation'],
    'Amount': [actual_spending_formatted, consolidated_operation_formatted],
    'Unique AWBs': [unique_awbs_total, num_weeks]
})

# Streamlit app
st.title('Shipping Cost Comparison')
st.write('Comparison of Actual Spending vs Consolidated Operation')

# Display the comparison DataFrame
st.write(comparison_df)

# Display repeated AWBs count
st.write(f"Number of Repeated AWBs: {repeated_awbs}")

# Display projected savings in a box
st.info(f"Projected Savings: {projected_savings_formatted}")

# Rearrange data for plotting
monthly_unique_awbs_df = monthly_unique_awbs.reset_index()
monthly_unique_awbs_df['Month'] = monthly_unique_awbs_df['Ship Date'].dt.strftime('%Y-%m')
monthly_unique_awbs_df = monthly_unique_awbs_df[['Month', 'Waybill Nbr - Ship Warehouse']]
monthly_unique_awbs_df = monthly_unique_awbs_df.set_index('Month')

# Display line chart for unique AWBs variation
st.title('Unique AWBs Variation (Monthly)')
st.write('Number of Unique AWBs over Time (Monthly)')
st.line_chart(monthly_unique_awbs_df)
