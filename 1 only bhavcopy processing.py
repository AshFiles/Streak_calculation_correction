import csv
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def process_csv():
    # Create a root window and hide it
    root = Tk()
    root.withdraw()

    # Ask the user to choose a CSV file with a custom title
    input_file = askopenfilename(title="Choose the bhavcopy file", filetypes=[("CSV Files", "*.csv")])

    if not input_file:
        print("No file selected. Exiting.")
        return

    # Read the CSV file
    with open(input_file, 'r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        data = list(csv_reader)

    # Remove spaces from headers and data cells
    headers = [header.replace(" ", "") for header in headers]
    data = [[cell.replace(" ", "") for cell in row] for row in data]

    # Get indices of required columns
    required_columns = ["SYMBOL", "DATE1", "LAST_PRICE"]
    column_indices = [headers.index(col) for col in required_columns if col in headers]

    # Filter data to keep only required columns
    filtered_headers = [headers[i] for i in column_indices]
    filtered_data = [[row[i] for i in column_indices] for row in data]

    # Create output filename
    output_file = "bhavcopy_temp.csv"

    # Write the processed data to the new CSV file
    with open(output_file, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(filtered_headers)
        csv_writer.writerows(filtered_data)

    print(f"Processed file saved as: {output_file}")

if __name__ == "__main__":
    process_csv()
