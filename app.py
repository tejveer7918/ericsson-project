import streamlit as st
import pandas as pd
import os

UPLOAD_FOLDER = 'uploads/'
TRANSFORM_FOLDER = 'transformed/'

# Ensure upload and transform folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSFORM_FOLDER, exist_ok=True)

def get_short_names(excel_file):
    try:
        df = pd.read_excel(excel_file)
        short_names = df['Short name'].str.strip().unique().tolist()
        return short_names
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def transform_data(excel_file, selected_short_names):
    try:
        df = pd.read_excel(excel_file)

        # Strip whitespace from 'Short name' column
        df['Short name'] = df['Short name'].str.strip()

        result_df = pd.DataFrame()

        for short_name in selected_short_names:
            # Select the row corresponding to the short name
            selected_row = df[df["Short name"] == short_name].iloc[0]

            # Extract the date and time from column names, ignore unnamed columns
            dates_with_time = [col for col in df.columns[2:] if "Unnamed" not in col]
            unique_dates = sorted(set(date.split(',')[0].strip() for date in dates_with_time), key=lambda x: pd.to_datetime(x, dayfirst=True))

            # Create a list to store new rows with time and corresponding values
            new_data = []
            for i in range(24):
                time = f"{i:02d}:00"
                time_data = {"time": time}
                row_sum = 0

                for date_with_time in dates_with_time:
                    date_part = date_with_time.split(',')[0].strip()
                    time_part = date_with_time.split(',')[1].strip() if ',' in date_with_time else ''

                    if time_part == time:
                        try:
                            value = selected_row[date_with_time]
                            if isinstance(value, str):
                                try:
                                    value = float(value)
                                except ValueError:
                                    value = 0.0
                            row_sum += value
                        except KeyError:
                            value = 0.0
                        time_data[date_part] = value

                time_data["Grand Total"] = row_sum
                new_data.append(time_data)

            # Create a DataFrame from the transformed data
