import SymbolUpdater
import configparser
import pandas as pd
import glob
import os
import core.DownloadMinutes as getData

if __name__ == '__main__':
    # Clear screen prior to execution
    clear = lambda: os.system('cls')
    clear()

    # Config
    config = configparser.ConfigParser()
    config.read('./config/source.ini')
    # Data object
    data = getData.DownloadMinutes('./config/indicators.ini')
    # Update symbol list and fundamentals
    SymbolUpdater.downloadSymbolData()

    # Update csvs for all time frames
    existingSymbols = pd.read_csv(config['filepath']['symbolList'], header=None)
    data.Download("AMC", destination="D:\\00.Stocks\\Data\\", dataInterval="1min", dateFilter=True)
    exit()
    for count, symbol in enumerate(existingSymbols[0]):

        data.Download(symbol, destination="D:\\00.Stocks\\Data\\", dataInterval="5min", dateFilter=True)
        data.Download(symbol, destination="D:\\00.Stocks\\Data\\", dataInterval="15min", dateFilter=True)
        data.Download(symbol, destination="D:\\00.Stocks\\Data\\", dataInterval="60min", dateFilter=True)



    # Perform HOD analysis
