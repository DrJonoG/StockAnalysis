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
import configparser
from helpers import csvToPandas


class DownloadMinutes:
    def __init__(self, indicators='./config/indicators.ini', apiPath='./config/api.conf'):
        print("==> Datasource set to AlphaVantage")
        print("==> For personal use please set up your own free API key")
        print("==> For large scale downloads, a premium key is required.")
        print("==> Academic keys are available for free to students.")
        print("==> https://www.alphavantage.co/documentation/")
        # Use your own api key here. Read as a single line in a file api.conf
        self.apiKey = open(apiPath).readline().rstrip()

        self.indicators = configparser.ConfigParser()
        self.indicators.read(indicators)

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


    def Download(self, symbol, destination, dataInterval, dateFilter=True):
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
        """
        # Location of save path
        saveFile = destination + dataInterval[:-2] + '\\%s.csv' % (symbol)
        if os.path.isfile(saveFile):
            # File exists update
            loadDF = csvToPandas(saveFile, asc=False, unicode=True)
            latestDate = loadDF.index.max()
            now = datetime.datetime.now()

            totalMonths = (now.year - latestDate.year) * 12 + now.month - latestDate.month
            totalMonths += 1 # For overlaps
        else:
            totalMonths = 3

        currentMonth = 1
        currentYear = 1
        newData = pd.DataFrame()
        for i in range(0, totalMonths):
            print(datetime.datetime.now().strftime("%H:%M:%S") + f" ==> Processing {symbol} month {i+1} of {totalMonths}", end="\r")
            dataAddress = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=%s&interval=%s&slice=year%smonth%s&apikey=%s' % (symbol, dataInterval, currentYear, currentMonth, self.apiKey)
            # Get data
            rawData = self.GetRaw(dataAddress)
            # Ensure there is a return
            if rawData is None:
                with open(destination + '/error.csv', "a") as file:
                    file.write(symbol + ', No data found. \n')
                continue

            # Enclose with try, unknown errors may occur from remote site
            try:
                # Extract and format data
                if newData.empty:
                    newData = self.PriceDFSorter(rawData.text)
                else:
                    # Join
                    data = self.PriceDFSorter(rawData.text)
                    newData = pd.concat([newData,data], axis=0)
            except Exception:
                print("\n" + datetime.datetime.now().strftime("%H:%M:%S") + f" ====> Error downloading month {i+1} of {totalMonths} for {symbol}", end="\n")

            # Update the months
            if currentMonth == 12:
                currentYear += 1
                currentMonth = 0

            currentMonth += 1

        print("\n" + datetime.datetime.now().strftime("%H:%M:%S") + f" ==> Verifying {symbol} data and calculating indicators.", end="\r")
        # Replace missing date times
        newData = newData.resample(dataInterval).mean()
        # Sort
        newData = newData.sort_index(ascending=False)
        # Remove any errors
        newData = newData[[isinstance(newData.index[i], datetime.datetime) for i in range(len(newData))]]
        # Remove weekends
        newData = newData[newData.index.dayofweek < 5]
        # Remove out of hours (except pre and post market)
        newData = newData[(newData.index.time > datetime.time(4, 0)) & (newData.index.time < datetime.time(20, 00))]
        # Replace nan values previous value if price, or 0 if not
        newData['close'] = newData['close'].fillna(method='ffill')
        newData['open'] = newData['open'].fillna(newData['close'])
        newData['high'] = newData['high'].fillna(newData['close'])
        newData['low'] = newData['low'].fillna(newData['close'])
        newData['volume'] = newData['volume'].fillna(0)
        # Round to avoid unnecesary decimals
        newData = newData.round(2)
        # Calculate indicators
        newData = self.CalculateIndicators(newData)
        # inform
        print(datetime.datetime.now().strftime("%H:%M:%S") + f" ==> Verification and indicators for {symbol} complete.", end="\n")
        # Begin saving process
        print(datetime.datetime.now().strftime("%H:%M:%S") + f" ==> Saving {symbol}.", end="\r")
        if not os.path.isfile(saveFile):
            newData.to_csv(saveFile, index=True)
        else:
            # Read existing and convert datetime
            loadDF = csvToPandas(saveFile, asc=False, unicode=True)
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
        print(datetime.datetime.now().strftime("%H:%M:%S") + f" ==> {symbol} saved to {saveFile}", end="\n")

        return True


    def ComputeADX(self, high, low, close, lookback):
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0

        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
        atr = tr.rolling(lookback).mean()

        plus_di = 100 * (plus_dm.ewm(alpha = 1/lookback).mean() / atr)
        minus_di = abs(100 * (minus_dm.ewm(alpha = 1/lookback).mean() / atr))
        dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
        adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
        adx_smooth = adx.ewm(alpha = 1/lookback).mean()

        return plus_di, minus_di, adx_smooth

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

    def CalculateIndicators(self, df):
        # General indicators
        candleSize = df['high'] - df['low']
        candleBody = abs(df['open'] - df['close'])

        # Calculate the percentage of the wick
        wickSize = candleSize - candleBody
        df['wick%'] = round(wickSize / candleSize, 2) * 100

        # Calculate true range of candle
        df['atr'] = candleSize

        # Calculate price percentage change
        df['chg$'] = round(df['close'] - df['open'], 2)
        df['chg%'] = round(((df['close'] - df['open']) / df['open']), 4)

        # Calculate SMA
        for period in self.indicators['indicators']['sma'].split(","):
            # Reverse order and calculate the simple moving average
            df[str(period) + "MA"] = round(df['close'].iloc[::-1].rolling(int(period)).mean(), 2)
        # Calculate EMA
        for period in self.indicators['indicators']['ema'].split(","):
            # Reverse order and calculate exponential moving average
            df[str(period) + "EMA"] = round(df['close'].iloc[::-1].ewm(span=int(period), adjust=False).mean(), 2)

        # Determine market hours (0 premarket, 1 open market, 2 postmarket)
        df.loc[(df.between_time('04:00:00', '09:30:01').index), 'Market'] = 0
        df.loc[(df.between_time('09:30:01', '16:00:00').index), 'Market'] = 1
        df.loc[(df.between_time('16:00:01', '20:00:00').index), 'Market'] = 2

        # Calculate VWAP
        df = df.groupby(df.index.date, group_keys=False).apply(self.ComputeVWAP)
        df['vwap'] = df['vwap'].fillna(method='ffill')
        df.loc[(df.between_time('16:00:01', '09:29:59').index), 'vwap'] = 0

        # Calculate Bollinger
        df["BollingerMA"], df["BollingerUpper"], df["BollingerLower"] = self.ComputerBollinger(df.close.iloc[::-1], period=20, stdDev=2)

        # Calculate adx
        df["plus_di"], df["minus_di"], df["adx_smooth"] = self.ComputeADX(df.high.iloc[::-1], df.low.iloc[::-1], df.close.iloc[::-1], 14)

        # On balance volume
        df.loc[df["close"] > df["close"].shift(1), "Vol+-"] = df["volume"]
        df.loc[df["close"] < df["close"].shift(1), "Vol+-"] = df["volume"] * (-1)
        df.loc[df["close"] == df["close"].shift(1), "Vol+-"] = 0

        df["OBV"] = df["Vol+-"].cumsum()
        df.drop(["Vol+-"], axis=1, inplace=True)

        return df
