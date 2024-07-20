import csv
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows


def bhavcopy_processing():
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

    # Find the index of the "SERIES" column
    series_index = headers.index("SERIES")

    # Filter rows where "SERIES" is "EQ"
    data = [row for row in data if row[series_index] == "EQ"]

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
    

def load_and_clean_csv(file_path):
    """
    Load a CSV file and clean the column names and data cells by removing spaces.
    
    Args:
    file_path (str): Path to the CSV file.
    
    Returns:
    pandas.DataFrame: Cleaned data.
    """
    data = pd.read_csv(file_path)
    print(f"Original columns in {file_path}: {data.columns.tolist()}")
    data.columns = data.columns.str.replace(' ', '')
    data = data.apply(lambda x: x.str.replace(' ', '') if x.dtype == "object" else x)
    print(f"Cleaned columns in {file_path}: {data.columns.tolist()}")
    return data


original_file_name = ""


def process_tradesheet_file():
    global original_file_name
    
    # Process the initial transaction CSV file.    
    
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Select the transaction CSV file downloaded from Streak",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    
    if file_path:    
        # Store the original file name without extension
        original_file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        data = load_and_clean_csv(file_path)
        data.dropna(how='all', inplace=True)
        
        symbols = []
        current_symbol = None
        
        for index, row in data.iterrows():
            if pd.notna(row['TriggerDate']) and 'NSE_' in str(row['TriggerDate']):
                current_symbol = str(row['TriggerDate']).replace('NSE_', '').replace('results', '')
            symbols.append(current_symbol)
        
        data.insert(0, 'SYMBOL', symbols)
        print("Added SYMBOL column to the transactions file.")
        
        data = data[~data['TriggerDate'].astype(str).str.contains('NSE_', na=False)]
        data.reset_index(drop=True, inplace=True)
        
        new_rows = []
        for symbol in data['SYMBOL'].unique():
            symbol_data = data[data['SYMBOL'] == symbol]
            if len(symbol_data) % 2 != 0:
                last_index = symbol_data.index[-1]
                last_row = symbol_data.iloc[-1]
                new_row = {
                    'SYMBOL': symbol,
                    'TriggerDate': '',
                    'TriggerTime': '',
                    'Buy/Sell': 'SELL',
                    'Quantity': -last_row['Quantity'],
                    'Price': '',
                    'CumulativeP&L': '',
                    'Triggertype': 'Manual'
                }
                new_rows.append((last_index, new_row))
        
        for last_index, new_row in sorted(new_rows, key=lambda x: x[0], reverse=True):
            data = pd.concat([data.iloc[:last_index + 1], pd.DataFrame([new_row]), data.iloc[last_index + 1:]], ignore_index=True)
        
        if 'Instrument' in data.columns:
            data.drop(columns=['Instrument'], inplace=True)
            print("Removed 'Instrument' column from the transactions file.")
        
        output_file_path = os.path.join(os.path.dirname(file_path), "transaction_details_temp.csv")
        try:
            data.to_csv(output_file_path, index=False)
            print(f"File processed and saved: {output_file_path}")
        except PermissionError:
            print(f"Permission denied: Unable to save the file. Please make sure the file '{output_file_path}' is not open or in use.")

    else:
        print("No transaction file selected")
  
        
def fill_empty_TriggerDate_and_Price_column():
    # Filling empty TriggerDate and Price column in the tradesheet csv file
    
    # Step 1: Automatically use 'bhavcopy_temp.csv' for the first CSV file
    bhavcopy_file = 'bhavcopy_temp.csv'

    # Step 2: Read the first file and extract the bhavcopy_date and last_price_dict
    bhavcopy_df = pd.read_csv(bhavcopy_file)
    bhavcopy_date = bhavcopy_df['DATE1'].iloc[0]
    last_price_dict = bhavcopy_df.set_index('SYMBOL')['LAST_PRICE'].to_dict()
    print(f"bhavcopy_date: {bhavcopy_date}")

    # Step 3: Automatically use 'transaction_details_temp.csv' for the second CSV file
    second_file = 'transaction_details_temp.csv'

    # Step 4: Read the second file
    second_df = pd.read_csv(second_file)

    # Fill empty values in the TriggerDate column with bhavcopy_date
    second_df['TriggerDate'] = second_df['TriggerDate'].fillna(bhavcopy_date)

    # Fill empty values in the Price column with the LAST_PRICE value based on the SYMBOL
    second_df['Price'] = second_df.apply(
        lambda row: last_price_dict[row['SYMBOL']] if pd.isna(row['Price']) and row['SYMBOL'] in last_price_dict else row['Price'],
        axis=1
    )

    # Save the modified second file with the same name, replacing the old one
    second_df.to_csv(second_file, index=False)
    
        
def fill_cumulative_profit_and_loss_column():
    csv_file = "transaction_details_temp.csv"
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Check if the necessary columns exist
    if 'CumulativeP&L' not in df.columns or 'Quantity' not in df.columns or 'Price' not in df.columns:
        print("The required columns are not present in the CSV file.")
        return
    
    # Fill missing values in the 'CumulativeP&L' column using the specified formula
    for i in range(1, len(df)):
        if pd.isna(df.at[i, 'CumulativeP&L']):
            df.at[i, 'CumulativeP&L'] = df.at[i-1, 'CumulativeP&L'] + (df.at[i-1, 'Quantity'] * (df.at[i, 'Price'] - df.at[i-1, 'Price']))
    
    # Save the updated DataFrame back to the same CSV file
    df.to_csv(csv_file, index=False)
    
    
def create_another_sheet_sum_profit_and_loss():
    global original_file_name
    
    file_path = 'transaction_details_temp.csv'
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print("File not found.")
        return

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Create a new DataFrame for profit and loss
    symbols = df['SYMBOL'].unique()
    profit_loss_data = {
        'SYMBOL': symbols,
        'no_of_trades': [len(df[df['SYMBOL'] == symbol]) / 2 for symbol in symbols],
        'p_and_l': [df[df['SYMBOL'] == symbol]['CumulativeP&L'].iloc[-1] for symbol in symbols]
    }
    profit_loss_df = pd.DataFrame(profit_loss_data)

    # Calculate totals
    total_trades = profit_loss_df['no_of_trades'].sum()
    total_p_and_l = profit_loss_df['p_and_l'].sum()
    
    # Add rows for totals and total after deductions
    total_row = pd.DataFrame([{'SYMBOL': 'Total', 'no_of_trades': total_trades, 'p_and_l': total_p_and_l}])
    deduction = total_trades * 75
    total_after_deductions = total_p_and_l - deduction
    deductions_row = pd.DataFrame([{'SYMBOL': 'Total after deductions', 'no_of_trades': '', 'p_and_l': total_after_deductions}])
    
    profit_loss_df = pd.concat([profit_loss_df, total_row, deductions_row], ignore_index=True)

    # Use the original file name to create the new Excel file
    excel_path = f'{original_file_name}.xlsx'

    # Create an Excel writer using openpyxl engine
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Write the original DataFrame to the first sheet
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        # Write the profit and loss DataFrame to the second sheet
        profit_loss_df.to_excel(writer, index=False, sheet_name='profit_and_loss')

    # Load the Excel file to rename the second sheet
    workbook = openpyxl.load_workbook(excel_path)
    sheet2 = workbook['profit_and_loss']
    sheet2.title = str(round(total_p_and_l))
    workbook.save(excel_path)

    # Delete the old CSV file
    os.remove(file_path)
    
    # Delete the bhavcopy_temp.csv file
    bhavcopy_path = 'bhavcopy_temp.csv'
    if os.path.exists(bhavcopy_path):
        os.remove(bhavcopy_path)

    print(f"Processed file saved as: {excel_path}")
    

if __name__ == "__main__":
    bhavcopy_processing()
    process_tradesheet_file()
    fill_empty_TriggerDate_and_Price_column()
    fill_cumulative_profit_and_loss_column()
    create_another_sheet_sum_profit_and_loss()
    print("All steps completed successfully.")