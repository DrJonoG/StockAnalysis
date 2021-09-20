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

class Alpha:
    def __init__(self, apiPath='./docs/api.conf'):
        print("==> Datasource set to AlphaVantage")
        print("==> For personal use please set up your own free API key")
        print("==> For large scale downloads, a premium key is required.")
        print("==> Academic keys are available for free to students.")
        print("==> https://www.alphavantage.co/documentation/")
        # Use your own api key here. Read as a single line in a file api.conf
        self.apiKey = open(apiPath).readline().rstrip()

    def GetDataFrame(self, dataAddress):
        try:
            # Open session and download
            with requests.Session() as session:
                # Get data
                rawData = session.get(dataAddress).text
                # Load as pandas and set index
                sessionDF = pd.read_csv(StringIO(rawData))
                # Replace names in headers
                sessionDF = sessionDF.rename(columns={'timestamp': 'Datetime', 'time': 'Datetime'})
                sessionDF = sessionDF.set_index('Datetime')
                # convert index to datetime
                sessionDF.index = pd.to_datetime(sessionDF.index)
                # Ensure ordering is consistent
                sessionDF = sessionDF[["open","close","high","low","volume"]]
        except Exception as e:
            print("==> Error occured retrieving data from Alpha: ")
            print(rawData)
            exit(0)

        return sessionDF

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

        # Need to convert from (i.e.) 5m to 5min
        if 'min' not in dataInterval:
            dataInterval += 'in'
        # Address for session
        dataAddress = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=%s&interval=%s&outputsize=full&apikey=%s&datatype=csv&adjusted=false' % (symbol, dataInterval, self.apiKey)
        # Get the requested data
        return self.GetDataFrame(dataAddress)


    def DownloadExtended(self, symbol, destination, dataInterval, month='*', year='*', merge=True):
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
        """

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

        mergedArr = []
        # Iterate through the yars and months to get data
        for y in yearRequest:
            for m in monthRequest:
                dataAddress = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=%s&interval=%smin&slice=year%smonth%s&apikey=%s' % (symbol, dataInterval, str(y), str(m), self.apiKey)
                sliceDF = self.GetDataFrame(dataAddress)
                if merge:
                    mergedArr.append(sliceDF)
                else:
                    sliceDF.to_csv(destination + '/%s_year_%s_month_%s.csv' % (sym, str(y), str(m)))

        # If merging the data, save here
        if merge:
            mergedDF = pd.concat(mergedArr)
            mergedDF.to_csv(destination + '/%s_full.csv' % (symbol))


    def Downloadfundamental(self):
        """
	    https://www.alphavantage.co/documentation/#fundamentals

        Parameters
        ----------

        """

    def DownloadIndicators(self):
        """
	    https://www.alphavantage.co/documentation/#technical-indicators

        Parameters
        ----------

        """
