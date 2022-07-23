
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

from helpers import csvToPandas, PrintProgressBar

def CalculateSlope(x,y):
    ## Prepare data
    X = x.values.astype(np.int64) // 10 ** 9 # for example, 2020-07-01 becomes 2020.49589041
    X = np.array(X) # convert list to a numpy array

    X -= X[0] # make it begin with 0.
    X = X[::,None] # convert row vector to column vector (just column vector is acceptable)
    y = y[::,None] # row vector to column vector (just column vector is acceptable)

    ## Apply linear regression
    reg = LinearRegression().fit(X, y) # start regression (X and y are both column vectors)
    slope = reg.coef_[0][0] # vslope of line (get first element from 2D array)
    intercept = reg.intercept_[0] # intercept with the y-axis (get first element from 1D array)

    fittedline = slope*X + intercept # generate prediction line (y=ax+b)
    fittedline = fittedline.flatten() # column vetor to row vector (just for displaying data)

    return slope, intercept, fittedline

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

    start_date = datetime.datetime(2020,1,1)
    df = df[df.index > start_date]
    # Check index is correct format
    if type(df.index) != pd.core.indexes.datetimes.DatetimeIndex: return

    # Filter out symbols that are penny stocks or too high in value
    #if df.close.min() > 80 or df.close.max() < 5: return

    dfPreMarket = df[df.Market == 0]
    # Open market only
    df = df[df.Market == 1]

    # Filter out data over a year old
    # Older dates have less signifcance as markets change
    #df = df[df.index >= '2022-01-01']

    # log file:
    fileName = 'ORB_Analysis.csv'
    if not os.path.exists(destination + fileName):
        with open(destination + fileName, "w") as f:
            f.write("Date,Symbol,PreVolume,ORType,preHigh,preLow,yestHigh,yestLow,Breaktime,ORPattern,Up,Down,Even,UpVol,DownVol,EvenVol,ORL,ORH,OR,OR%,ATR,ORas%ofATR,ATR>OR,ORL>yHOD,ORC>yHOD,ORH>PreHigh,ORH>PreLow,HigherVolOnEntry,>EMA50,>EMA100,50MA>100MA,VWAP>50EMA,Entry,Stop,StopType,RiskPerShare,PT1,PT1-time,P1Met,PT2,PT2-time,P2Met,Figure\n")
    f = open(destination + fileName, 'a')
    """ Parameters """
    # Stop details
    risk = 200
    # Where is OR in relation to yesterday
    yHigh = 0
    yLow = 0
    # Total counters
    totalWins = 0
    totalLosses = 0
    totalBars = 0
    # Number of bars in the open range
    ORBars = 5
    # counter for current day
    dayCount = 0
    # ATR
    atrList = list()
    # Iterate through each day
    for idx, day in df.groupby(df.index.date):

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

        if(len(Date) < 300):
            continue

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
        figure.AddLine(day, "vwap", "orange", "VWAP",1)
        figure.AddLine(day, "50EMA", "blue", "50EMA",1)

        figure.AddStopLine(Date[0], Date[len(Date)-1], yHigh, "yH", '#90ee90', 0.3)
        figure.AddStopLine(Date[0], Date[len(Date)-1], yLow, "yL", '#FF7E62', 0.3)

        # Update variables
        yestHigh = yHigh
        yestLow = yLow

        # OR based on open close
        ORL = round(min(day[0:ORBars].low),2)
        ORH = round(max(day[0:ORBars].high),2)

        # Is the close of the OR (i.e., close of 5 minutes on OR5) above yesterdays high
        ORClosePosition = 0
        if Close[ORBars] > yHigh:
            ORClosePosition = 1
        elif Close[ORBars] < yLow:
            ORClosePosition = -1

        # Is the low of the OR greater than yesterdays high
        ORLowPosition = 0
        if ORL > yHigh:
            ORLowPosition = 1
        elif ORL < yLow:
            ORLowPosition = -1

        # Update high and low now that they have been used
        # This is ready for the next iteration
        yLow = min(day.low.to_numpy())
        yHigh = max(day.high.to_numpy())

        # EMA indicators
        above50EMA = 0
        above100EMA = 0
        # Is the ORH greater than the moving averages
        if ORH > trendFast[0]:
            above50EMA = 1
        if ORH > trendSlow[0]:
            above100EMA = 1

        # Whether moving averages are stacked on each other
        MAStacked = 0
        if trendFast[0] > trendSlow[0]:
            MAStacked = 1

        # Whether vwap is above fast MA
        VwapAboveFast = 0
        if VWAP[0] > trendFast[0]:
            VwapAboveFast = 1

        # Premarket data
        preMarket = dfPreMarket[dfPreMarket.index.date == idx]
        # Error checking
        if len(preMarket.index) == 0:
            continue
        # Premarket values
        preMarketHigh = max(preMarket.high)
        preMarketLow = min(preMarket.low)
        preMarketVol = sum(preMarket.volume.to_numpy())

        # Add pre-market levels
        figure.AddStopLine(Date[0], Date[len(Date)-1], preMarketHigh, "preH", '#90ee90', 0.6)
        figure.AddStopLine(Date[0], Date[len(Date)-1], preMarketLow, "preL", '#FF7E62', 0.6)

        # Exclude low pre-market volume
        if preMarketVol < 1000000:
            continue

        positionInPre = 0 # 0 is inside, 1 above pre market highs, -1 below
        # Check where ORH is in relation to premarket
        if ORH > preMarketHigh:
            positionInPre = 1
        elif ORH < preMarketLow:
            positionInPre = -1

        positionInPreLow = 0 # 0 is inside, 1 above pre market lows, -1 below
        # Check where ORL is in relation to premarket
        if ORL > preMarketLow:
            positionInPreLow = 1
        elif ORL < preMarketLow:
            positionInPreLow = -1

        # Trade variables, reset to defaults
        breakAbove = False
        breakBelow = False
        stopLoss = 0
        entryPrice = 0
        riskPerShare = 0
        profitOne = 0
        profitTwo = 0
        profitOneMet = False
        profitTwoMet = False
        profitOneTime = "None"
        profitTwoTime = "None"
        stoppedOut = False
        drawFigure = False
        breakTime = None
        P1Met = 0
        P2Met = 0
        HigherVolOnEntry = 0 # 0 means no, 1 means yes
        stopType = "Min"

        # Do not continue if open range is 0
        if ORH == ORL:
            continue

        Up = 0
        Down = 0
        Even = 0

        UpVol = 0
        DownVol = 0
        EvenVol = 0

        ORType = ""

        ORPattern = ""
        for j in range(0,ORBars):
            if Close[j] > Open[j]:
                ORPattern = ORPattern + " 1"
                Up += 1
                UpVol += Vol[i]
            elif Close[j] < Open[j]:
                ORPattern = ORPattern + " -1"
                Down += 1
                DownVol += Vol[i]
            else:
                ORPattern = ORPattern + " 0"
                Even += 1
                EvenVol += Vol[i]

        # Iterate through the candlesticks of the current day
        for i in range(ORBars, len(Low)):
            if not breakAbove and not breakBelow:
                # If break not found within an hour, stop
                if i >= 60 + ORBars:
                    break;

                if Close[i] > Open[i]:
                    ORPattern = ORPattern + " 1"
                    Up += 1
                elif Close[i] < Open[i]:
                    ORPattern = ORPattern + " -1"
                    Down += 1
                else:
                    ORPattern = ORPattern + " 0"
                    Even += 1

                # Look for break above OR
                if High[i] > ORH and Open[i] > VWAP[i]:
                    entryPrice = ORH + 0.02
                    stopLoss = Low[i] - 0.01
                    riskPerShare = round((entryPrice - stopLoss),2)

                    # Don't risk under 0.05 and Don't risk more than $0.35
                    if riskPerShare < 0.06:
                        break
                    else:
                        stopType = "EntryCandle"

                    # Higher average volume on entry?
                    # Skip first two bars due to market opening
                    if Volume[i] > np.average(Volume[ORBars-3:ORBars]):
                        HigherVolOnEntry = 1

                    # Set targets
                    profitOne = round((riskPerShare * 2.0) + entryPrice,2)
                    profitTwo = round((riskPerShare * 3.0) + entryPrice,2)

                    # Add to figure
                    #figure.AddStopLine(Date[0], Date[i], ORL, "ORL", 'grey', 0.5)
                    #figure.AddStopLine(Date[0], Date[i], ORH, "ORH", 'grey', 0.5)
                    #figure.AddStopLine(Date[0], Date[len(Date)-1], profitOne, "PT1", 'grey', 0.5)
                    #figure.AddStopLine(Date[0], Date[len(Date)-1], profitTwo, "PT2", 'grey', 0.5)
                    #figure.AddStopLine(Date[0], Date[len(Date)-1], stopLoss, "Stop", 'grey', 0.5)
                    figure.AddMarker(Date[i], entryPrice, 'triangle-up', 'green', "", size=16)

                    breakTime = Date[i]
                    breakAbove = True
                    drawFigure = True
                    ORType = "Long"
                    continue
                else if Low[i] < ORL and Open[i] < VWAP[i]:
                    entryPrice = ORL - 0.02
                    stopLoss = High[i] + 0.01
                    riskPerShare = round((stopLoss - entryPrice),2)

                    # Don't risk under 0.05 and Don't risk more than $0.35
                    if riskPerShare < 0.06:
                        break
                    else:
                        stopType = "EntryCandle"

                    # Higher average volume on entry?
                    # Skip first two bars due to market opening
                    if Volume[i] > np.average(Volume[ORBars-3:ORBars]):
                        HigherVolOnEntry = 1

                    # Set targets
                    profitOne = round(entryPrice - (riskPerShare * 2.0) ,2)
                    profitTwo = round(entryPrice - (riskPerShare * 3.0) ,2)

                    # Add to figure
                    #figure.AddStopLine(Date[0], Date[i], ORL, "ORL", 'grey', 0.5)
                    #figure.AddStopLine(Date[0], Date[i], ORH, "ORH", 'grey', 0.5)
                    #figure.AddStopLine(Date[0], Date[len(Date)-1], profitOne, "PT1", 'grey', 0.5)
                    #figure.AddStopLine(Date[0], Date[len(Date)-1], profitTwo, "PT2", 'grey', 0.5)
                    #figure.AddStopLine(Date[0], Date[len(Date)-1], stopLoss, "Stop", 'grey', 0.5)
                    figure.AddMarker(Date[i], entryPrice, 'triangle-down', 'red', "", size=16)

                    breakTime = Date[i]
                    breakBelow = True
                    drawFigure = True
                    ORType = "Short"
                    continue
            elif breakAbove:
                if(High[i] >= profitOne and not profitOneMet):
                    # profit target met
                    profitOneMet = True
                    P1Met = 1
                    profitOneTime = Date[i].strftime("%H:%M")
                    # Add exit to figure
                    figure.AddMarker(Date[i], profitOne, 'triangle-down', 'blue', str(profitOne) , size=16)
                if(High[i] >= profitTwo and not profitTwoMet):
                    # profit target met
                    profitTwoMet = True
                    P2Met = 1
                    profitTwoTime = Date[i].strftime("%H:%M")
                    # Add exit to figure
                    figure.AddMarker(Date[i], profitTwo, 'triangle-down', 'blue', str(profitTwo) , size=16)
                    break
                # Check if we're stopped out
                if(Low[i] < stopLoss):
                    # Lost trade
                    stoppedOut = True
                    # Add exit to figure
                    figure.AddMarker(Date[i], stopLoss, 'triangle-down', 'red', 'SL', size=16)
                    break
            elif breakBelow:
                if(Low[i] <= profitOne and not profitOneMet):
                    # profit target met
                    profitOneMet = True
                    P1Met = 1
                    profitOneTime = Date[i].strftime("%H:%M")
                    # Add exit to figure
                    figure.AddMarker(Date[i], profitOne, 'triangle-up', 'blue', str(profitOne) , size=16)
                if(Low[i] <= profitTwo and not profitTwoMet):
                    # profit target met
                    profitTwoMet = True
                    P2Met = 1
                    profitTwoTime = Date[i].strftime("%H:%M")
                    # Add exit to figure
                    figure.AddMarker(Date[i], profitTwo, 'triangle-up', 'blue', str(profitTwo) , size=16)
                    break
                # Check if we're stopped out
                if(High[i] > stopLoss):
                    # Lost trade
                    stoppedOut = True
                    # Add exit to figure
                    figure.AddMarker(Date[i], stopLoss, 'triangle-up', 'green', 'SL', size=16)
                    break
                # Check if we're stopped out
                if(Low[i] < stopLoss):
                    # Lost trade
                    stoppedOut = True
                    # Add exit to figure
                    figure.AddMarker(Date[i], stopLoss, 'triangle-down', 'red', str(stopLoss) + ' (Stopped out)', size=16)
                    break
            else if breakBelow:
                if(Low[i] <= profitOne and not profitOneMet):
                    # profit target met
                    profitOneMet = True
                    P1Met = 1
                    profitOneTime = Date[i].strftime("%H:%M")
                    # Add exit to figure
                    figure.AddMarker(Date[i], profitOne, 'triangle-down', 'blue', str(profitOne) + ' (P 1.50)', size=16)
                if(Low[i] <= profitTwo and not profitTwoMet):
                    # profit target met
                    profitTwoMet = True
                    P2Met = 1
                    profitTwoTime = Date[i].strftime("%H:%M")
                    # Add exit to figure
                    figure.AddMarker(Date[i], profitTwo, 'triangle-down', 'blue', str(profitTwo) + ' (P 2.0)', size=16)
                    break
                # Check if we're stopped out
                if(High[i] > stopLoss):
                    # Lost trade
                    stoppedOut = True
                    # Add exit to figure
                    figure.AddMarker(Date[i], stopLoss, 'triangle-down', 'red', str(stopLoss) + ' (Stopped out)', size=16)
                    break

        if drawFigure:
            fileLocation = "None"
            # Name figure for easy sorting
            figName = "Loss_"
            if P1Met == 1:
                figName = "Profit_"
            fileLocation = destination + "/figures/" + figName + "_" + symbol + "_" + str(ORType) + "_" + str(idx) + ".png"
            figure.Save(fileLocation)

            OR = round(ORH-ORL,2)
            ORPercent = round(OR / Close[0], 4)
            atrAboveOR = 0
            if ATR >= OR:
                atrAboveOR = 1
            ORPercentOfATR = round(OR / ATR, 4)


            f.write(f"{idx},{symbol},{preMarketVol},{ORType},{preMarketHigh},{preMarketLow},{yestHigh},{yestLow},{breakTime.strftime('%H:%M')},{ORPattern},{Up},{Down},{Even},{UpVol},{DownVol},{EvenVol},{ORL},{ORH},{OR},{ORPercent},{ATR},{ORPercentOfATR},{atrAboveOR},{ORLowPosition},{ORClosePosition},{positionInPre},{positionInPreLow},{HigherVolOnEntry},{above50EMA},{above100EMA},{MAStacked},{VwapAboveFast},{entryPrice},{stopLoss},{stopType},{riskPerShare},{profitOne},{profitOneTime},{P1Met},{profitTwo},{profitTwoTime},{P2Met},{fileLocation}\n")
