import pandas as pd
import openpyxl
import os
from openpyxl.utils.dataframe import dataframe_to_rows

def sum_pnl_create_another_sheet():
    # this sums up the total profit and loss, and show that data on another sheet in excel
    
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

    # Add a row for the sum of p_and_l
    total_p_and_l = profit_loss_df['p_and_l'].sum()
    total_row = pd.DataFrame([{'SYMBOL': 'Total', 'no_of_trades': '', 'p_and_l': total_p_and_l}])
    profit_loss_df = pd.concat([profit_loss_df, total_row], ignore_index=True)

    # Create the path for the new Excel file
    excel_path = 'transactions_after_manual_exit_' + str(round(total_p_and_l)) + '.xlsx'

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
    sum_pnl_create_another_sheet()
