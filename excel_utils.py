import pandas as pd
import os
from datetime import datetime

def save_results_to_excel(df, output_dir="results", base_name="CSP_Phase2_Results"):
    """
    Save a DataFrame to an Excel file with a timestamp in the filename.
    Returns the path to the saved file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{base_name}_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)

    df.to_excel(filepath, index=False)
    return filepath
