__author__ = 'DrJonoG'  # Jonathon Gibbs

#
# Copyright 2016-2020 Cuemacro - https://www.jonathongibbs.com / @DrJonoG
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and limitations under the License.
#

import os
import requests
import time
import pandas as pd
import datetime
from helpers import PrintProgressBar, LoadTickerNames
import numpy as np
import data.Yahoo
import data.Alpha

class DownloadData:
    """
        #Summary:
            Downloads financial data from a list of symbols currentlty supports:
                Yahoo
                AlphaVantage (In part)
        #Complete
            Implement initial SymbolData class
            Ability to choose between download data or process on the fly
            Add support for Yahoo
            Comment
            Moved data sources to individual files
        #TODO:
            Add support for more sources
            Add support for more markets (i.e. crypto)
            Multi-threading on downloading files to improve speed
    """

    def __init__(self, source="alpha"):
        # Determine source
        if source.lower() == 'yahoo':
            self.dataSource = data.Yahoo.Yahoo()
        elif source.lower() == 'alpha':
            self.dataSource = data.Alpha.Alpha()
        else:
            self.dataSource = data.Alpha.Alpha()


    def Download(self, dataRange, dataInterval, symbolList, column=0, destinationPath=None):
        """
	    Takes a list of either symbol names or a csv to a list of symbol names. If destinationPath is specified then data is saved, else temporary storage in a dataframe.
        If file already exists (destinationPath) then the file is updated and overwritten.

        Parameters
        ----------
        dataRange : String
            The range (i.e. 60d) for which to obtain data
        dataInterval : String
            The time period for which to obtain data (i.e. 5m)
        symbolList : String[]
            A list of symbols to download either csv files or strings
        column : Int
            The column in which the symbol is located, 0 by default. For CSV lists only.
        source : String
            Where to obtain the quote data from
        destinationPath : String:
            Where to save symbol data. If none, data is not saved and instead stored in variable
        """
        start = time.time()

        # If saving, make folders
        if destinationPath:
            if not os.path.exists(destinationPath):
                os.makedirs(destinationPath)

        # Load in the ticker list
        tickers = pd.Series(dtype="float64")

        # Iterate list and load csv if file list, or append string otherwise
        for t in symbolList:
            if os.path.isfile(t):
                tickers = tickers.append(LoadTickerNames(t, column), ignore_index=True).drop_duplicates()
            else:
                tickers = tickers.append(pd.Series(t), ignore_index=True)
        tickerCount = len(tickers)

        # Dictionary to return data if not saving
        symbolData = {}
        # Iterate through each of the tickers and download data
        for index, symbol in tickers.items():
            try:
                if destinationPath:
                    if not os.path.exists(destinationPath + symbol + ".csv"):
                        df = self.dataSource.Download(symbol, dataRange, dataInterval)
                        df.to_csv(destinationPath + symbol + ".csv")
                    else:
                        self.dataSource.Update(symbol, dataInterval, destinationPath + symbol + ".csv")
                else:
                    df = self.dataSource.Download(symbol, dataRange, dataInterval)
                    symbolData[symbol] = df.reset_index()
                PrintProgressBar(index, tickerCount, prefix = '==> Downloded: ' + symbol.ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            except Exception as e:
                # Can fail for numerous reasons including unavailable ticker, server down etc,.
                PrintProgressBar(index, tickerCount, prefix = '==> Failed   : ' + symbol.ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            PrintProgressBar(tickerCount, tickerCount, prefix = '==> Downloading complete ', suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
        return symbolData


    def Update(self, dataInterval, folderLocation):
        """
	    Update a folder without the need to specify specific symbol names

        Parameters
        ----------
        dataInterval : String
            The time period for which to obtain data (i.e. 5m)
        folderLocation : String:
            Where the master files are to update
        """
        start = time.time()

        # Check if folder exists
        if not os.path.exists(folderLocation):
            return "Error: Folder not found"

        # Get all files
        allFiles = os.listdir(folderLocation)
        fileList = list(filter(lambda f: f.endswith('.csv'), allFiles))
        fileCount = len(fileList)
        # Iterate through each file (essentially each of the symbols)
        for index, filename in enumerate(fileList):
            # Symbol name
            symbol = filename.split('.')[0]
            # Display progress
            PrintProgressBar(index, fileCount, prefix = '==> Updating: ' + symbol.ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            # Update
            self.dataSource.Update(symbol, dataInterval, folderLocation + filename)
        PrintProgressBar(index, tickerCount, prefix = '==> Updating data complete', suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
