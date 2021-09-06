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

from pathlib import Path
from helpers import PrintProgressBar
import datetime
import numpy as np
import pandas as pd
import os
import time

class ComputeIndicators(object):
    """
        #Summary:
            Calculates various technical indicators and associated trading signals.
        #Complete
            RSI
            VWAP
            Bollinger
            Moving averages
            Exponential moving averages
        #TODO:
            Add more indicators
            Ability to process on the fly as opposed to saving
            Improve efficiency
    """
    def __init__(self, **argd):
        self.__dict__.update(argd)

    def ComputeRSI(self, diff):
        """
	    Computers the relative strength idnex

        Parameters
        ----------
        diff : Series
            First discrete difference of element

        """
        # Preserve dimensions off diff values
        upChange = 0 * diff
        downChange = 0 * diff
        # up change is equal to the positive difference, otherwise equal to zero
        upChange[diff > 0] = diff[ diff>0 ]
        # down change is equal to negative deifference, otherwise equal to zero
        downChange[diff < 0] = diff[ diff < 0 ]
        # values are related to exponential decay
        # we set com=rsiLength-1 so we get decay alpha=1/rsiLength
        upChangeAvg   = upChange.ewm(com=self.rsiLength-1 , min_periods=self.rsiLength).mean()
        downChangeAvg = downChange.ewm(com=self.rsiLength-1 , min_periods=self.rsiLength).mean()
        # Calculate RSI value
        return round(100 - (100 / (abs(upChangeAvg/downChangeAvg)+1)), self.precision)

    def ComputerBollinger(self, close, period, stdDev):
        """
	    Computers bollinger bands for given period and standard deviation
        See https://en.wikipedia.org/wiki/Bollinger_Bands for more information

        Parameters
        ----------
        close : Series
            A pandas series of close prices

        period: Int
            Time period to apply bollinger bands

        stdDev: Float
            Standard deviation of upper and lower bands

        """
        # Calculate moving average and standard deviation on stock close
        movingAverage = close.rolling(period).mean()
        standardDeviation = close.rolling(period).std()
        # Calculate upper and lower bands based on stdDev multiplier
        bollingerUpper = movingAverage + standardDeviation * stdDev
        bollingerLower = movingAverage - standardDeviation * stdDev
        return [movingAverage, bollingerUpper, bollingerLower]

    def ComputeVWAP(self, df):
        """
	    Computers volume-weighted average price
        See https://en.wikipedia.org/wiki/Volume-weighted_average_price for more information

        Parameters
        ----------
        df : Dataframe
            Dataframe containing the volume and close for a series of data

        """
        volume = df.volume
        close = df.close
        return round(df.assign(vwap=(close * volume).cumsum() / volume.cumsum()),2)

    def Indicators(self, tickerDF):
        # Convert to datetime
        tickerDF['Datetime']= pd.to_datetime(tickerDF['Datetime'])
        # Replace nan values previous value if price, or 0 if not
        tickerDF['close'] = tickerDF['close'].fillna(method='ffill')
        tickerDF['open'] = tickerDF['open'].fillna(tickerDF['close'])
        tickerDF['high'] = tickerDF['high'].fillna(tickerDF['close'])
        tickerDF['low'] = tickerDF['low'].fillna(tickerDF['close'])
        # Candle direction (bull or bear)
        tickerDF['Candle'] = (tickerDF['close'] - tickerDF['open']).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        # Calculate moving_averages
        for period in self.simpleMovingAverage:
            tickerDF[str(period) + "MA"] = round(tickerDF['close'].rolling(period).mean(), self.precision)
        for period in self.expMovingAverage:
            tickerDF[str(period) + "EMA"] = round(tickerDF['close'].ewm(span=period, adjust=False).mean(), self.precision)
        # Calculate RSI
        if self.rsiLength > 0:
            tickerDF["RSI" + str(self.rsiLength)] = self.ComputeRSI(tickerDF.close.diff(1))
        # Calculate bollinger bands
        if self.bollingerPeriod > 0:
            tickerDF["BollingerMA"], tickerDF["BollingerUpper"], tickerDF["BollingerLower"] = self.ComputerBollinger(tickerDF.close, self.bollingerPeriod, self.bollingerStdDev)
        # Calculate VWAP
        if self.vWAP:
            tickerDF = tickerDF.groupby(tickerDF['Datetime'].dt.date, group_keys=False).apply(self.ComputeVWAP)
        # Replace NaN with 0
        tickerDF = tickerDF.fillna(0)
        return tickerDF

    def ComputeForFiles(self, source, destination=None):
        """
	    Computer the specified indicators for each file within the source folder

        Parameters
        ----------
        source : String
            A path to the directory containing the raw (downloaded) csv files. Files should contain columns for Datetime, open, close, high, low

        destination : String
            A path to the destination where files with computed indicators will be saved

        """

        # Get file list
        files = list(Path(source).rglob('*.csv'))
        fileCount = len(files)
        # Iterate through each of the csv files
        start = time.time()
        for index, fileName in enumerate(files):
            tickerDF = pd.read_csv(fileName)
            # File name
            fileName = Path(fileName).name
            PrintProgressBar(index+1, fileCount, prefix = 'Progress: ' + str(fileName).ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            tickerDF = self.Indicators(tickerDF)
            # Save
            tickerDF.to_csv(destination + fileName, index=True)

    def ComputeForDF(self, dataframes, destination):
        """
	    Computer the specified indicators for each file within the source folder

        Parameters
        ----------
        dataframes : Dictionary
            A dictionary of pandas dataframes which should contain columns for Datetime, open, close, high, low

        """
        dfCount = len(dataframes)
        indicatorDF = {}
        # Iterate through each of the csv files
        start = time.time()
        for index, value in enumerate(dataframes):
            PrintProgressBar(index+1, dfCount, prefix = 'Progress:  ' + str(value).ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            # Get dataframe
            df = dataframes[value]
            # Calculate the indicators
            indicatorDF[value] = self.Indicators(df)
            # If destination is specified, save the dataframe
            if destination:
                indicatorDF[value].to_csv(destination + value + ".csv", index=True)

        return indicatorDF

    def Compute(self, source, destination=None):
        """
        Computer the indicators. Accepts either or a folder to the location of csv files

        Parameters
        ----------
        source : String / Dictionary
            A dictionary of pandas dataframes
            or
            A path to the directory containing the raw (downloaded) csv files. Files should contain columns for Datetime, open, close, high, low

        destination : String
            A path to the destination where files with computed indicators will be saved

        """
        # Check if destination exists
        if destination and not os.path.exists(destination):
            os.makedirs(destination)
        if type(source) is dict:
            return self.ComputeForDF(source, destination)
        else:
            self.ComputeForFiles(source, destination)
