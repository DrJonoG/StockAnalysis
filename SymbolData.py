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
import glob
import requests
import time
import pandas as pd
import arrow
import datetime
from helpers import PrintProgressBar

class SymbolData:
    """
        #Summary:
            Downloads financial data from a list of symbols currentlty supports:
                Yahoo
        #Complete
            Implement initial SymbolData class
            Ability to choose between download data or process on the fly
            Add support for Yahoo
            Comment
        #TODO:
            Add support for more sources
            Add support for more markets (i.e. crypto)
            Multi-threading on merging files to improve speed
    """

    def __init__(self, destinationPath=""):
        # File paths
        self.destinationPath = destinationPath

    def LoadTickerNames(self, filepath, column=0):
        """
	    Loads in a list of tickets from a csv file.

        Parameters
        ----------
        filepath : String
            Location of the csv file containing a list of symbol names

        column : Int
            The column in which the symbol is located, 0 by default.

        """
        # Symbol must be first column
        df = pd.read_csv(filepath)
        return df.iloc[:, column]

    def GetQuoteData(self, symbol, dataRange, dataInterval, source="yahoo"):
        """
	    Downloads data for a single symbol

        Parameters
        ----------
        symbol : String
            The symbol which to obtain quote data for
        dataRange : String
            The range (i.e. 60d) for which to obtain data

        dataInterval : String
            The time period for which to obtain data (i.e. 5m)

        source : String
            Where to obtain the quote data from

        """
        if source == "yahoo":
            # Yahoo prevents access now; use a header to mimic human access
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            # Access data
            res = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=%s' % (symbol, dataRange, dataInterval),headers=headers)
            data = res.json()
            body = data['chart']['result'][0]
            # Create datetime index
            dt = datetime.datetime
            dt = pd.Series(map(lambda x: arrow.get(x).to('US/Eastern').datetime.replace(tzinfo=None), body['timestamp']), name='Datetime')
            df = pd.DataFrame(body['indicators']['quote'][0], index=dt)

        return df

    def DownloadSymbolData(self, dataRange, dataInterval, symbolList, column=0, source="yahoo", destinationPath=None):
        """
	    Takes a list of either symbol names or a csv to a list of symbol names. If destinationPath is specified then data is saved, else temporary storage in a dataframe.

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
            Where to save symbol data. If none, data is not saved.

        """
        if destinationPath:
            destinationPath = destinationPath + datetime.datetime.today().strftime('%Y-%m-%d') + '/'
            if not os.path.exists(destinationPath):
                os.makedirs(destinationPath)

        # Load in the ticker list
        tickers = pd.Series(dtype="float64")

        # Iterate list and load csv if file list, or append string otherwise
        for t in symbolList:
            if os.path.isfile(t):
                tickers = tickers.append(self.LoadTickerNames(t, column), ignore_index=True).drop_duplicates()
            else:
                tickers = tickers.append(pd.Series(t), ignore_index=True)
        tickerCount = len(tickers)

        # Dictionary to return data if not saving
        symbolData = {}
        # Iterate through each of the tickers and download data
        start = time.time()
        for index, value in tickers.items():
            try:
                df = self.GetQuoteData(value, dataRange, dataInterval, source)
                # Ensure ordering is consistent
                df = df[["open","close","high","low","volume"]]
                if destinationPath:
                    df.to_csv(destinationPath + value + "_" + dataInterval + ".csv", index=True)
                else:
                    symbolData[value] = df.reset_index()
                PrintProgressBar(index+1, tickerCount, prefix = 'Downloded: ' + value.ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            except Exception as e:
                # Can fail for numerous reasons including unavailable ticker, server down etc,.
                PrintProgressBar(index+1, tickerCount, prefix = 'Failed   : ' + value.ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))

        return symbolData

    def MergeDataFiles(self, sourcePath, masterDestination):
        """
        Merges files of the same time frame and symbol together.
        Used when data is regularly downloaded as lookback of Yahoo is only 60 days on 5minute interval

        Parameters
        ----------
        sourcePath : String
            A directory containing the directories of symbols to merge

        masterDestination : String
            The location in which to store the merged files

        """
        folderList = [ f.path for f in os.scandir(sourcePath) if f.is_dir() ]
        if len(folderList) > 1:
            if not os.path.exists(masterDestination):
                os.makedirs(masterDestination)
            # Use glob module to return all csv files under root directory. Create DF from this.
            fileList = pd.DataFrame([file for file in glob.glob(sourcePath + "/*/*")], columns=["fullpath"])
            # Split the full path into directory and filename and join with original into one DataFrame
            fileList = fileList['fullpath'].str.rsplit("\\", 1, expand=True).rename(columns={0: 'path', 1:'filename'}).join(fileList)
            # List of unique files
            uniqueFiles = fileList['filename'].unique()
            countUnique = len(uniqueFiles)
            # Iterate over unique filenames; read CSVs, concat DFs, save file
            start = time.time()
            for i, f in enumerate(uniqueFiles):
                PrintProgressBar(i, countUnique, prefix = 'Merging: '  + f.ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
                pathList = fileList[fileList['filename'] == f]['fullpath'] # Get list of fullpaths from unique filenames
                dfs = [pd.read_csv(path) for path in pathList] # Get list of dataframes from CSV file paths
                dfConcat = pd.concat(dfs) # Concat dataframes into one
                dfConcat = dfConcat.drop_duplicates(subset=['Datetime'], keep='first').reset_index(drop=True) # Remove duplicate entries
                dfConcat = dfConcat.set_index(pd.DatetimeIndex(dfConcat['Datetime'])).sort_index()
                dfConcat.to_csv(masterDestination + f, index=False) # Save dataframe
