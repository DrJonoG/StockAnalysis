__author__ = 'DrJonoG'  # Jonathon Gibbs

#
# Copyright 2016-2020 https://www.jonathongibbs.com / @DrJonoG
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
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
import datetime
import numpy as np
import pandas as pd
import os
from threading import Thread
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
            Ability to process on the fly as opposed to saving
            Remove holidays and out of hours
        #TODO:
            Add more indicators
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

    def Indicators(self, tickerDF, marketOnly, frequency):
        """
	    Computer indicators on tickerDF

        Parameters
        ----------
        tickerDF : Dataframe
            Pandas dataframe for one symbol
        marketOnly : Bool
            If true show only open market hours. Else show pre- and post-market hours too
        frequency : String
            Frequency for the function date range, specifying the frequency of times
        """
        # Convert to datetime
        tickerDF['Datetime'] = pd.to_datetime(tickerDF['Datetime'])
        # Sort dates old to new
        tickerDF = tickerDF.sort_values(by='Datetime', ascending=True).reset_index()
        # Replace missing date times
        start = tickerDF['Datetime'].iloc[0]
        end = tickerDF['Datetime'].iloc[-1]
        # Set datetime to index
        tickerDF = tickerDF.set_index('Datetime').drop(columns=['index'])
        '''
            Some data sources do not return rows where the volume is 0. To calculate accurate
            moving averages etc,. all times need to be visible. Inserting rows is computationally
            expense, thus we create an empty datarange and merge the two together.
        '''
        # Get all times between start and end date with a frequency of freq
        dateDF = pd.date_range(start=start, end=end, freq=frequency)
        # Remove weekends
        dateDF = dateDF[dateDF.dayofweek < 5]
        # Remove out of hours (except pre and post market)
        dateDF = dateDF[(dateDF.time > datetime.time(4, 0)) & (dateDF.time <= datetime.time(20, 00))]
        # Get a list of holidays between the start and end
        USHolidays =  calendar().holidays(start=start, end=end)
        # Remove public holidays
        m = dateDF.isin(USHolidays) # TODO check this
        dateDF = dateDF[~m].copy()
        # Convert DatetimeIndex to dataframe
        dateDF = pd.DataFrame(index=dateDF)
        # Join dataframe to maintin all dates
        tickerDF =  dateDF.join(tickerDF)
        # Filter out if only market open hours
        if marketOnly:
            # Filter times
            dateDF = dateDF[(dateDF > datetime.time(9, 30)) & (dateDF < datetime.time(16, 00))]
            tickerDF = tickerDF[(tickerDF.index.time > datetime.time(9, 30)) & (tickerDF.index.time < datetime.time(16, 00))]
            # Determine market hours (0 premarket, 1 open market, 2 postmarket)
            tickerDF.loc[(tickerDF.between_time('09:30:01', '16:00:00').index), 'Market'] = 1
        else:
            # Filter times
            dateDF = dateDF[(dateDF > datetime.time(4, 0)) & (dateDF < datetime.time(20,0))]
            tickerDF = tickerDF[(tickerDF.index.time > datetime.time(4, 0)) & (tickerDF.index.time < datetime.time(20,0))]
            # Determine market hours (0 premarket, 1 open market, 2 postmarket)
            tickerDF.loc[(tickerDF.between_time('04:00:00', '09:30:01').index), 'Market'] = 0
            tickerDF.loc[(tickerDF.between_time('09:30:01', '16:00:00').index), 'Market'] = 1
            tickerDF.loc[(tickerDF.between_time('16:00:01', '20:00:00').index), 'Market'] = 2
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
            tickerDF = tickerDF.groupby(tickerDF.index.date, group_keys=False).apply(self.ComputeVWAP)
            tickerDF['vwap'] = tickerDF['vwap'].fillna(method='ffill')
            tickerDF.loc[(tickerDF.between_time('16:00:01', '09:29:59').index), 'vwap'] = 0
        # Replace NaN with 0
        tickerDF = tickerDF.fillna(0)
        # Sort dates old to new
        tickerDF = tickerDF.sort_index(ascending=False)
        # return indicators
        return tickerDF


    def ComputeThread(self, fileList, marketOnly, destination, frequency):
        for index, fileName in enumerate(fileList):
            # Load small sample of csv to check for update
            tickerDF = pd.read_csv(fileName, nrows=2)
            # Skip if file does not contain datetime
            if ('Datetime' not in tickerDF.columns): continue
            # If update required, load full file:
            tickerDF = pd.read_csv(fileName, sep=',', parse_dates=["Datetime"], encoding= 'unicode_escape', dayfirst = True, infer_datetime_format=True, engine='c', na_filter=False, usecols=['Datetime','open', 'close', 'high', 'low', 'volume'])
            # Ensure more than 0 rows
            if len(tickerDF.index) > 0:
                # File name
                fileName = Path(fileName).name
                # Check if already been updated, and skip if so.
                if ('Market' not in tickerDF.columns) or (tickerDF.head(1).Market.values not in [0,1,2]):
                    # Compute indicators
                    tickerDF = self.Indicators(tickerDF, marketOnly, frequency)
                    # Save
                    tickerDF.to_csv(destination + fileName, index=True, index_label="Datetime")
                else:
                    # Copy file anyway so all files are in single location
                    tickerDF.to_csv(destination + fileName, index=False)


    def ComputeForFiles(self, source, marketOnly, destination, frequency):
        """
	    Computer the specified indicators for each file within the source folder

        Parameters
        ----------
        source : String
            A path to the directory containing the raw (downloaded) csv files. Files should contain columns for Datetime, open, close, high, low
        destination : String
            A path to the destination where files with computed indicators will be saved
        marketOnly : Bool
            If true show only open market hours. Else show pre- and post-market hours too
        frequency : String
            Frequency for the function date range, specifying the frequency of times
        """
        # Get file list
        files = list(Path(source).rglob('*.csv'))
        fileCount = len(files)
        # Split files for multi threaded
        cores = 12
        fileSplit = np.array_split(np.array(files),cores)
        # multi thread
        threads = []
        for i in range(0, cores):
            threads.append(Thread(target=self.ComputeThread, args=([fileSplit[i],marketOnly, destination, frequency])))

        print(f"==> Processing indicators over {cores} cores. Please be patient.")
        start = time.time()
        # Start all threads
        for x in threads:
            x.start()

        # Wait for all of them to finish
        for x in threads:
            x.join()

        PrintProgressBar(fileCount, fileCount, prefix = '==> Indicators complete  ', suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))


    def ComputeForDF(self, dataframes, marketOnly, destination=None):
        """
	    Computer the specified indicators for each file within the source folder

        Parameters
        ----------
        dataframes : Dictionary
            A dictionary of pandas dataframes which should contain columns for Datetime, open, close, high, low
        destination : String
            A path to the destination where files with computed indicators will be saved
        marketOnly : Bool
            If true show only open market hours. Else show pre- and post-market hours too
        """
        dfCount = len(dataframes)
        indicatorDF = {}
        # Iterate through each of the csv files
        start = time.time()
        for index, value in enumerate(dataframes):
            PrintProgressBar(index, dfCount, prefix = '==> Progress:  ' + str(value).ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            # Get dataframe
            df = dataframes[value]
            # Calculate the indicators
            indicatorDF[value] = self.Indicators(df, marketOnly)
            # If destination is specified, save the dataframe
            if destination:
                indicatorDF[value].to_csv(destination + value + ".csv", index=True)
        PrintProgressBar(dfCount, dfCount, prefix = '==> Indicators complete  ', suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))

        return indicatorDF


    def Compute(self, source, frequency, update=False, destination=None, marketOnly=False):
        """
        Computer the indicators. Accepts either a dictionary of stock data or a folder to the location of csv files

        Parameters
        ----------
        source : String / Dictionary
            A dictionary of pandas dataframes
            or
            A path to the directory containing the raw (downloaded) csv files. Files should contain columns for Datetime, open, close, high, low
        frequency : String
            Frequency for the function date range, specifying the frequency of times
        update : Bool
            Whether the files should be udpated
        destination : String
            A path to the destination where files with computed indicators will be saved
        marketOnly : Bool
            If true show only open market hours. Else show pre- and post-market hours too
        """
        # Check if destination exists
        if destination and not os.path.exists(destination):
            os.makedirs(destination)

        if type(source) is dict:
            return self.ComputeForDF(source, destination, marketOnly)
        else:
            if update:
                self.ComputeForFilesUpdate(source, marketOnly, destination, frequency)
            else:
                self.ComputeForFiles(source, marketOnly, destination, frequency)
            return True
