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
import time
import pandas as pd
import arrow
import numpy as np
import urllib.request, json

class Yahoo:
    def __init__(self):
        print("==> Datasource set to Yahoo")
        print("==> Yahoo has known issues with retriving 100% of the data")
        print("==> Please check your data once downloaded to confirm it is complete")

    def FilterDataRange(self, dataRange, dataInterval):
        """
        Enforce the datacap set by Yahoo
        Returns: the maximum datarange provided by Yahoo if requested range is over the maximum

        Parameters
        ----------
        dataRange : Int
            The data range being requested
        dataInterval : String
            The interval of data requested
        """
        # Maximum of 7 days for 1 minute
        if dataInterval == '1m' and dataRange > 7:
            return 7
        # Maximum of 60 days for any other minutes
        if 'm' in dataInterval and dataRange > 60:
            return 60
        # Maximum of 365 for daily
        if 'y' in dataInterval:
            return 365

        return str(dataRange) + 'd'

    def Download(self, symbol, dataRange, dataInterval):
        """
	    Downloads data for a single symbol
        Returns: a dataframe ordered datetime, open, close, high, low, volume

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

        with requests.Session() as session:
            # Yahoo prevents access now; use a header to mimic human access
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            # Access data
            data = session.get('https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=%s' % (symbol, dataRange, dataInterval),headers=headers).json()
            body = data['chart']['result'][0]
            # Create datetime index
            dt = pd.Series(map(lambda x: arrow.get(x).to('US/Eastern').datetime.replace(tzinfo=None), body['timestamp']), name='Datetime')
            df = pd.DataFrame(body['indicators']['quote'][0], index=dt)
            # Ensure ordering is consistent
            df = df[["open","close","high","low","volume"]]
            # Return the downloaded data
        return df

    def Update(self, symbol, dataInterval, sourcePath):
        """
	    Update a single symbol

        Parameters
        ----------
        symbol : String
            The name of the symbol to update
        dataInterval : String
            The time period for which to obtain data (i.e. 5m)
        sourcePath : String:
            Where the master files are to update
        """

        # Confirm file does exist
        if not os.path.exists(sourcePath):
            return "Error: No files found"

        # Find the last entry in the file
        masterDF = pd.read_csv(sourcePath)
        lastEntry = datetime.datetime.strptime(masterDF['Datetime'].iloc[-1], '%Y-%m-%d %H:%M:%S').date()
        # Define data range based on last entry and get data
        dataRange = np.busday_count(lastEntry, datetime.datetime.today().strftime('%Y-%m-%d')) - 1
        # Filter the range to match the caps of yahoo
        dataRange = self.FilterDataRange(dataRange, dataInterval)
        # Download data
        df = self.Download(symbol, dataRange, dataInterval)
        # Update dataframe
        df = df[df.index > masterDF['Datetime'].iloc[-1]]
        masterDF = masterDF.append(df.reset_index(), ignore_index = True)
        # Save and overwrite previous
        masterDF.to_csv(sourcePath, index=False)
