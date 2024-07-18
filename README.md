# Streak_calculation_correction
A simple script to work upon transactions of streak to counter the market exit scenario

You should have two files to run the script:

1. Download the Transaction details file from Streak once the backtest is done
2. Download the "Full Bhavcopy and Security Deliverable date" from NSE website at https://www.nseindia.com/all-reports (Go to Archives option to download for a particular date)

Run each script one by one indicated by their order of execution in their file names.
First it will ask for the bhavcopy file, then it will ask for the transaction details file.
Make sure all the files including the two csv files and the scripts are in the same folder.

The distinct feature of the bhavcopy file is that it has columns named as SYMBOL, DATE1 and LAST_PRICE