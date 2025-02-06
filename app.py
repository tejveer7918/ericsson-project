import streamlit as st
import pandas as pd
import os
import zipfile

# Set maximum upload size (in megabytes)
st.set_option('server.maxUploadSize', 200)

def get_short_names(excel_file):
    try:
        df = pd.read_excel(excel_file)
        short_names = df['Short name'].str.strip().unique().tolist()
        return short_names
    except Exception as e:
        st.error(f"An error occurred while extracting short names: {e}")
        return []

def transform_data(excel_file, selected_short_names):
    try:
        df = pd.read_excel(excel_file)

        # Strip whitespace from 'Short name' column
        df['Short name'] = df['Short name'].astype(str).str.strip()

        result_df = pd.DataFrame()

        for short_name in selected_short_names:
            # Select the row corresponding to the short name
            selected_row = df[df["Short name"] == short_name]

            if selected_row.empty:
                st.warning(f"Short name '{short_name}' not found in the Excel file.")
                continue

            selected_row = selected_row.iloc[0]

            # Extract the date and time from column names, ignore unnamed columns
            dates_with_time = [col for col in df.columns[2:] if "Unnamed" not in col]
            unique_dates = sorted(
                set(date.split(',')[0].strip() for date in dates_with_time),
                key=lambda x: pd.to_datetime(x, dayfirst=True)
            )

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
            temp_df = pd.DataFrame(new_data, columns=["time"] + unique_dates + ["Grand Total"])
            temp_df["Short Name"] = short_name

            # Append to result DataFrame
            result_df = pd.concat([result_df, temp_df], ignore_index=True)

        return result_df

    except Exception as e:
        st.error(f"An error occurred during data transformation: {e}")
        return None

def main():
    st.title("Excel Transformer")

    # Upload file section
    uploaded_file = st.file_uploader("Upload Excel or Zip File", type=["xlsx", "zip"])

    if uploaded_file is not None:
        try:
            extracted_files = []

            if uploaded_file.name.endswith(".zip"):
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    zip_ref.extractall()
                    extracted_files = [f for f in zip_ref.namelist() if f.endswith(".xlsx")]
            else:
                # Save uploaded file to disk
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                extracted_files = [uploaded_file.name]

            all_short_names = []
            for excel_file in extracted_files:
                all_short_names.extend(get_short_names(excel_file))

            all_short_names = list(set(all_short_names))  # Remove duplicates

            if not all_short_names:
                st.error("No short names found in the uploaded file(s).")
                return

            selected_short_names = st.multiselect("Select Short Names", all_short_names)

            if st.button("Transform"):
                if not selected_short_names:
                    st.warning("Please select at least one short name.")
                    return

                result_df = pd.DataFrame()
                for excel_file in extracted_files:
                    transformed_df = transform_data(excel_file, selected_short_names)
                    if transformed_df is not None:
                        result_df = pd.concat([result_df, transformed_df], ignore_index=True)

                if not result_df.empty:
                    # Convert DataFrame to Excel in memory
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        result_df.to_excel(writer, index=False)
                    processed_data = output.getvalue()

                    st.success("Transformation complete! Click below to download.")
                    st.download_button(
                        label="Download Transformed File",
                        data=processed_data,
                        file_name="transformed_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("No data to download.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
