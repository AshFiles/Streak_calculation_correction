import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

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

def process_file(file_path):
    """
    Process the initial transaction CSV file.
    
    Args:
    file_path (str): Path to the CSV file containing transaction data.
    
    Returns:
    pandas.DataFrame: Processed transaction data.
    """
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
    
    return data

def main():
    """
    Main function to run the script.
    """
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Select the transaction CSV file downloaded from Streak",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    
    if file_path:
        data = process_file(file_path)
        
        output_file_path = os.path.join(os.path.dirname(file_path), "transaction_details_temp.csv")
        try:
            data.to_csv(output_file_path, index=False)
            print(f"File processed and saved: {output_file_path}")
        except PermissionError:
            print(f"Permission denied: Unable to save the file. Please make sure the file '{output_file_path}' is not open or in use.")
    else:
        print("No transaction file selected")

if __name__ == "__main__":
    main()
