
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

# TODO: improve efficiency

import os
import time
import random
import datetime
import numpy as np
import pandas as pd
import matplotlib.lines as lines
import matplotlib.pyplot as plt
import plotly.offline as po
import financialanalysis as fa
from core import Figure
from pathlib import Path
from sklearn.linear_model import LinearRegression
from analysis import CandlestickPatterns as finder
from helpers import csvToPandas, PrintProgressBar

def Analyse(symbol, source, destination, marketOnly=True):
    """
    A series of possible variables to be tested

    Parameters
    ----------
    symbol : String
        The path to the csv file to analyse
    destinationPath : String
        Path to where to save the analysis
    marketOnly : Bool
        A boolean to use only market opening hours (if true) or all times (if false)
    """

    # Load DF
    if not os.path.exists(source + symbol): return
    df = csvToPandas(source + symbol)

    # Filter out data over a year old
    # Older dates have less signifcance as markets change
    start_date = datetime.datetime(2022,1,1)
    df = df[df.index > start_date]
    # Check index is correct format
    if type(df.index) != pd.core.indexes.datetimes.DatetimeIndex: return

    # Premarket data
    dfPreMarket = df[df.Market == 0]

    # log file:

    """ Parameters """
    # Where is OR in relation to yesterday
    yHigh = 0
    yLow = 0
    # Number of bars in the open range
    ORBars = 5
    # counter for current day
    dayCount = 0
    # ATR
    atrList = list()
    # Iterate through each day
    for idx, day in df.groupby(df.index.date):
        day = day[day.index.hour < 15]
        day = day[day.index.hour > 6]

        Low = day.low.to_numpy()
        High = day.high.to_numpy()

        if High.shape[0] < 1:
            continue

        # Skip first 14 days to get accurate ATR
        # Enough data that this won't matter
        if dayCount < 14:
            # Insert range
            atrList.insert(0,max(High) - min(Low))
            dayCount += 1

            # Get high and low values
            # This will be previous day high and low once dayCount is reached
            yLow = min(day.low.to_numpy())
            yHigh = max(day.high.to_numpy())

            continue

        # Premarket data
        preMarket = dfPreMarket[dfPreMarket.index.date == idx]
        # Error checking
        if len(preMarket.index) == 0:
            continue
        # Premarket values
        preMarketHigh = max(preMarket.high)
        preMarketLow = min(preMarket.low)
        preMarketVol = sum(preMarket.volume.to_numpy())


        # Exclude low pre-market volume
        if preMarketVol < 2000000:
            continue

        # Calculate the average
        ATR = round(np.average(atrList),2)

        # Insert ready for next interation
        # This is done after ATR is calculated to avoid look forward
        atrList.insert(0,max(High) - min(Low))
        atrList.pop(14)

        # Pandas to numpy
        Volume = day.volume.to_numpy()

        # check if average volume below min volume
        # This is look forward, however, I wouldn't trade stocks without a high pre-market
        # Consequently, 3million volume is an easy target.
        #if sum(Volume) < 3000000:
        #    continue

        # Convert columns to numpy
        Date = day.index.time

        CandleDir = day.Candle.to_numpy()
        Close = day.close.to_numpy()
        Open = day.open.to_numpy()
        Vol = day.volume.to_numpy()
        VWAP = day.vwap.to_numpy()
        trendFast = day['50EMA'].to_numpy()
        trendSlow = day['100EMA'].to_numpy()
        # Filter out symbols that are penny stocks or too high in value
        if max(High) < 5: continue

        # Create figure
        figure = Figure.Figure()
        figure.CandleStick(day)
        figure.TextConfig(chartTitle=f"{symbol} : {idx}")
        #figure.AddLine(day, "vwap", "orange", "VWAP",1)
        figure.AddLine(day, "50EMA", "blue", "50EMA",2)
        figure.AddLine(day, "20EMA", "grey", "20EMA",1)

        # Add pre-market levels
        figure.AddStopLine(Date[0], Date[len(Date)-1], preMarketHigh, "preH", '#90ee90', 0.6)
        figure.AddStopLine(Date[0], Date[len(Date)-1], preMarketLow, "preL", '#FF7E62', 0.6)
        #figure.AddStopLine(Date[0], Date[len(Date)-1], yHigh, "yH", '#90ee90', 0.3)
        #figure.AddStopLine(Date[0], Date[len(Date)-1], yLow, "yL", '#FF7E62', 0.3)

        # Iterate through the candlesticks of the current day
        for i in range(1, len(Low)-1):
            if finder.doji(day, i):
                figure.AddStopLine(Date[i-1], Date[i+1], High[i], "doji")

        # Update variables
        yestHigh = yHigh
        yestLow = yLow

        # Update high and low now that they have been used
        # This is ready for the next iteration
        yLow = min(day.low.to_numpy())
        yHigh = max(day.high.to_numpy())



        figure.addText(preMarketHigh, preMarketLow, yHigh, yLow)
        fileLocation = destination + symbol + "_" + str(idx) + ".png"
        figure.Save(fileLocation)
