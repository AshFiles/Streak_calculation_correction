# Streak_calculation_correction
A simple script to work upon transactions of streak backtest to handle the market exit scenario.
Right now the streak backtest is not showing the profit or loss for the stocks which have still not exited the market.
We are assuming that on our choice of date (for which we will download the bhavcopy), we will exit the market for all the stocks which are active all at once.
The price at which we are exiting the market is going to be the day's last traded price.

You should have two files to run the script:

1. Download the Transaction details file from Streak once the backtest is done
2. Download the "Full Bhavcopy and Security Deliverable date" from NSE website at https://www.nseindia.com/all-reports (Go to Archives option to download for a particular date)

Run theh script indicated by the .py file.
First it will ask for the bhavcopy file, then it will ask for the transaction details file.
Make sure all the files including the two csv files and the scripts are in the same folder.

The distinct feature of the bhavcopy file is that it has columns named as SYMBOL, DATE1 and LAST_PRICE