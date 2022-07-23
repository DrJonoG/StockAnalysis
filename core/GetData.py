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

import requests
import pandas as pd
import numpy as np
from io import StringIO
import os
import time
import datetime
from helpers import csvToPandas


class GetData:
    def __init__(self, apiPath='./config/api.conf'):
        print("==> Datasource set to AlphaVantage")
        print("==> For personal use please set up your own free API key")
        print("==> For large scale downloads, a premium key is required.")
        print("==> Academic keys are available for free to students.")
        print("==> https://www.alphavantage.co/documentation/")
        # Use your own api key here. Read as a single line in a file api.conf
        self.apiKey = open(apiPath).readline().rstrip()

    def GetRaw(self, dataAddress):
        """
	    Downloads the raw data from the data address specified
        Returns: Raw response from address

        Parameters
        ----------
        dataAddress : String
            The url request for data from AlphaVantage
        """
        try:
            # Open session and download
            with requests.Session() as session:
                # Get data
                rawData = session.get(dataAddress)
                return rawData
        except Exception as e:
            print("==> Error occured retrieving data from Alpha: ")
            print(e)
            return None

    def PriceDFSorter(self, rawData):
        """
	    Processes raw text data from request response into pandas dataframe
        Returns: Dataframe

        Parameters
        ----------
        rawData : String
            Raw text response from AlphaVantage
        """
        try:
            # Load as pandas and set index
            sliceDF = pd.read_csv(StringIO(rawData))
            # Replace names in headers
            sliceDF = sliceDF.rename(columns={'timestamp': 'Datetime', 'time': 'Datetime'})
            sliceDF = sliceDF.set_index('Datetime')

            # convert index to datetime
            sliceDF.index = pd.to_datetime(sliceDF.index)
            # Ensure ordering is consistent and return
            sliceDF = sliceDF[["open","close","high","low","volume"]]
            return sliceDF
        except Exception as e:
            return None

    def Download(self, symbol, dataRange, dataInterval):
        """
	    Downloads data for a single symbol using the standard time series intraday call
        For full intraday history (~2 years) use DownloadExtended
        Returns: a dataframe ordered datetime, open, close, high, low, volume

        Parameters
        ----------
        symbol : String
            The symbol which to obtain quote data for
        dataRange : String
            The required month and year
        dataInterval : String
            The time period for which to obtain data (i.e. 5m)
        """

        # Address for session
        dataAddress = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=%s&interval=%s&outputsize=full&apikey=%s&datatype=csv&adjusted=false' % (symbol, dataInterval, self.apiKey)

        # Get the requested data
        rawData = self.GetRaw(dataAddress)
        # Ensure there is a return
        if rawData is None:
            with open(destination + '/error.csv', "a") as file:
                file.write(symbol + ', No data found. \n')
            return None
        # Extract and format data
        sessionDF = self.PriceDFSorter(rawData.text)
        return sessionDF




    def DownloadExtended(self, symbol, destination, dataInterval, month='*', year='*', merge=True, skipExisting=False, dateFilter=True):
        """
	    https://www.alphavantage.co/documentation/#intraday-extended

        Parameters
        ----------
        symbol : String
            The symbol in which to obtain quote data for
        destination : String
            The location where the files should be saved
        dataInterval : Int
            The time period
        month : String
            The month to obtain data for, '*' for all data.
        year : String
            The year to obtain data for, '*' for all data.
        merge : Bool
            Whether to merge the files if * is used, or save them individually
        """
        # Location of save path
        saveFile = destination + '/%s.csv' % (symbol)

        # If skip existing return
        if skipExisting and os.path.isfile(saveFile):
            return False

        # Get the requested months and store in an array
        if month == '*':
            monthRequest = [m for m in range(1, 13)]
        else:
            monthRequest = [month]

        # Get request years and store in an array
        if year == '*':
            yearRequest = [y for y in range(1, 3)]
        else:
            yearRequest = [year]

        # Iterate through the yars and months to get data
        for y in yearRequest:
            for m in monthRequest:
                dataAddress = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=%s&interval=%s&slice=year%smonth%s&apikey=%s' % (symbol, dataInterval, str(y), str(m), self.apiKey)
                # Get data
                rawData = self.GetRaw(dataAddress)
                # Ensure there is a return
                if rawData is None:
                    with open(destination + '/error.csv', "a") as file:
                        file.write(symbol + ', No data found. \n')
                    continue
                # Extract and format data
                newData = self.PriceDFSorter(rawData.text)
                # Check if data was retrieved, if not, return.
                if newData is None:
                    continue
                # Merge or save
                if merge:
                    if not os.path.isfile(saveFile):
                        newData.to_csv(saveFile, index=True)
                    else:
                        # Read existing and convert datetime
                        loadDF = csvToPandas(saveFile, asc=False, unicode=True)
                        if len(loadDF) == 0:
                            continue
                        if dateFilter:
                            # Get latest date and filter
                            maxDate = max(loadDF.index)
                            newData = newData[newData.index > maxDate]
                        # If new data, then save
                        if len(newData) > 0:
                            # Join
                            newData = pd.concat([newData,loadDF], axis=0)
                            # Drop duplicates and sort
                            newData = newData[~newData.index.duplicated(keep='first')]
                            newData = newData.sort_index(ascending=False)
                            # Overwrite file
                            newData.to_csv(saveFile, index=True)
                else:
                    newData.to_csv(destination + '/%s_year_%s_month_%s.csv' % (symbol, str(y), str(m)))

        return True


    def Downloadfundamental(self, symbol, filePath):
        """
	    https://www.alphavantage.co/documentation/#fundamentals
        Downloads fundamental data for the symbol and saves as a csv.
        It does not check for duplicates when writing

        Parameters
        ----------
        symbol : String
            The symbol in which to obtain quote data for
        filePath : String
            The location where the files should be saved
        """
        dataAddress = 'https://www.alphavantage.co/query?function=OVERVIEW&symbol=%s&apikey=%s' % (symbol, self.apiKey)
        # Get the requested data and error checking
        try:
            rawData = self.GetRaw(dataAddress).json()
        except Exception as e:
            with open(filePath.replace(".csv", "_errors.csv"), "a") as file:
                file.write(symbol + ', ' + e + ' -> Dataddress: ' + dataAddress + '\n')
            return
        # If error message returned, or no data available, skip and append to error file
        if 'Error Message' in rawData:
            with open(filePath.replace(".csv", "_errors.csv"), "a") as file:
                file.write(symbol + ', ' + rawData['Error Message'] + '\n')
            return
        if len(rawData) == 0:
            with open(filePath.replace(".csv", "_errors.csv"), "a") as file:
                file.write(symbol + ', No data found. \n')
            return
        # Transpose pandas series
        df = pd.Series(rawData).to_frame().T
        df = df.replace(',','', regex=True)
        # Write to csv
        if not os.path.isfile(filePath):
           df.to_csv(filePath, index=False)
        else: # else it exists so append without writing the header
           df.to_csv(filePath, mode='a', index=False, header=False)

        # `SharesOutstanding`, `SharesFloat`, `SharesShort`, `SharesShortPriorMonth`, `ShortRatio`, `ShortPercentOutstanding`, `ShortPercentFloat`,
        # `PercentInsiders`, `PercentInstitutions`, `ForwardAnnualDividendRate`, `ForwardAnnualDividendYield`, `PayoutRatio`, `DividendDate`, `ExDividendDate`

    def DownloadIndicators(self, symbol, indicator, interval, period, ohlc):
        """
	    https://www.alphavantage.co/documentation/#technical-indicators

        Parameters
        ----------
        symbol : String
            The symbol in which to obtain quote data for
        indicator : String
            Indictator to download chosen from:
                SMA, EMA, WMA, VWAP, MACD, RSI, ADX, BBANDS, ATR, OBV

        """
        dataAddress = 'https://www.alphavantage.co/query?function=%s&symbol=%s&interval=%s&time_period=%s&series_type=%s&apikey=%s' % (indicator, symbol, interval, period, ohlc, self.apiKey)
        # Get the requested data
        rawData = self.GetRaw(dataAddress).text

    def EarningDates(self, symbol=None):
        # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
        if symbol:
            dataAddress = 'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol=%s&horizon=3month&apikey=%s' % (symbol, self.apiKey)
        else:
            dataAddress = 'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=3month&apikey=%s' % self.apiKey
        # Get the requested data
        rawData = self.GetRaw(dataAddress).text


    def TimeFrame(self, group):
        pass

    # Alphavantage does not offer extended data for all time frames
    # Function to create specific minute data from downloaded 1 minute intraday
    def CalculateMinutes(self, symbol, timeFrame, destinationPath, path):
        filePath = path + symbol + '.csv'
        destination = destinationPath + symbol + '.csv'
        # Check source file exists
        if not os.path.exists(filePath): return
        # Load source
        tickerDF = csvToPandas(filePath, asc=False, unicode=True)
        start_date = datetime.datetime(2022,1,1)
        tickerDF = tickerDF[tickerDF.index > start_date]

        # Load custom time
        if os.path.exists(destination):
            customDF = csvToPandas(destination, asc=False, unicode=True)
            if len(customDF) > 0:
                # Get latest date from existing data and filter to remove duplicates
                maxDate = max(customDF.index)
                tickerDF = tickerDF[tickerDF.index > maxDate]

        # New time frame
        newTF = []
        # check length
        if len(tickerDF) < 3:
            return

        # Group
        tickerGroups = tickerDF.groupby(pd.Grouper(freq=timeFrame, offset='1min'))#.apply(your_function)

        counter = 0
        for name, group in tickerGroups:
            if len(group) <= 1:
                continue
            row = [max(group.index), group.iloc[0][0], group.iloc[-1][1], max(group.high), min(group.low), int(float(group.volume[0])) + int(float(group.volume[1]))]
            newTF.append(row)

        # Convert to df
        df = pd.DataFrame(newTF, columns = ['Datetime','open','close','high','low','volume'])
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df = df.set_index('Datetime')


        if os.path.exists(destination):
            # Join
            df = pd.concat([customDF,df], axis=0)
        # Order
        df = df.sort_index(ascending=False)
        # Save
        df.to_csv(destination)
