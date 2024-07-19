import pandas as pd

def fill_cumulative_pnl_column(csv_file):
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
    print(f"Updated CSV file saved: {csv_file}")

if __name__ == "__main__":
    csv_file = "transaction_details_temp.csv"
    fill_cumulative_pnl(csv_file)
