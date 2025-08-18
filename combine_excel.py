import pandas as pd
import os

def combine_files(file_list, output_path="temp/combined.xlsx"):
    all_data = []

    for file in file_list:
        try:
            df = pd.read_excel(file)
            all_data.append(df)
        except Exception as e:
            print(f"⚠️ Could not read {file}: {e}")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df.to_excel(output_path, index=False)
        return output_path
    else:
        return None
