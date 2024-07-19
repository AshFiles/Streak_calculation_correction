import pandas as pd

def main():
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
    print(f"Modified file saved as: {second_file}")

if __name__ == "__main__":
    main()
