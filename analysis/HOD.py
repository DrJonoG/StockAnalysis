
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
import pathlib
import numpy as np
import pandas as pd
import matplotlib.lines as lines
import matplotlib.pyplot as plt
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

def OpenFile(path,y,m,d):
    # Open 5 minute chart
    if not os.path.exists(path): return
    df = csvToPandas(path)

    start_date = datetime.datetime(y,m,d)
    df = df[df.index > start_date]

    return df

def WriteLine(year,time, longshort, orperc, vwapperc,WithinPreRange,AbovePreH,BelowPreLow,WithinYRange,AboveYHigh,BelowYLow, loss, pt1Met, pt2Met, risk):
    # Counts
    winners = pt1Met
    total = loss + winners

    # Write to file
    lossVal = loss * risk
    pt1Val = (pt1Met * (risk * 2))
    pt2Val = (pt2Met* (risk * 3))
    winVal = pt1Val
    totalVal = lossVal + pt1Val

    if lossVal == 0:
        lossVal = 1

    if total > 0:
        winperc = round(winners/(winners+loss),2)
        valperc = round(winVal / totalVal , 2)
    else:
        winperc = 0
        valperc = 0

    new_row = [year,time, longshort,orperc, vwapperc, WithinPreRange,AbovePreH,BelowPreLow,WithinYRange,AboveYHigh,BelowYLow, total, winners, loss,winperc,pt1Met, pt2Met, winVal - lossVal, round(winVal / lossVal,2) ,lossVal, winVal, pt1Val, pt2Val, valperc]
    return new_row

def AnalysePerTicker(path, filename, outputfile):
    fullDF = pd.read_csv(path + filename, index_col = 0)
    risk = 1

    columns=['Year','Symbol','LongShort','Total','Wins','Losses','WinPerc','PT1','PT2','AvgPerTrade','LossVal','WinVal','PT1Val','PT2Val','WinValPerc']
    rows = []

    # Short
    df = fullDF[(fullDF.Entry < fullDF.Stop)]
    df_symbol = df.groupby('Symbol').agg({'Symbol':'count', 'P1Met':'sum', 'P2Met':'sum'})
    df_symbol = df_symbol.rename(columns={'Symbol': 'Total'}).reset_index()
    df_full = pd.DataFrame()
    df_full['Symbol'] = df_symbol['Symbol']
    df_full['LongShort'] = 'Short'
    df_full['Total'] = df_symbol['Total']
    df_full['Wins'] = df_symbol['P1Met'] + df_symbol['P2Met']
    df_full['Losses'] = df_full['Total'] - df_full['Wins']
    df_full['WinPerc'] = round((df_full['Wins'] / df_full['Total'])*100, 2)
    df_full['PT1'] = df_symbol['P1Met']
    df_full['PT2'] = df_symbol['P2Met']
    df_full['Total'] = df_symbol['Total']
    df_full['Total'] = df_symbol['Total']

    # Long
    df = fullDF[(fullDF.Entry >= fullDF.Stop)]
    df_symbol = df.groupby('Symbol').agg({'Symbol':'count', 'P1Met':'sum', 'P2Met':'sum'})
    df_symbol = df_symbol.rename(columns={'Symbol': 'Total'}).reset_index()
    df_full_l = pd.DataFrame()
    df_full_l['Symbol'] = df_symbol['Symbol']
    df_full_l['LongShort'] = 'Long'
    df_full_l['Total'] = df_symbol['Total']
    df_full_l['Wins'] = df_symbol['P1Met'] + df_symbol['P2Met']
    df_full_l['Losses'] = df_full_l['Total'] - df_full_l['Wins']
    df_full_l['WinPerc'] = round((df_full_l['Wins'] / df_full_l['Total'])*100, 2)
    df_full_l['PT1'] = df_symbol['P1Met']
    df_full_l['PT2'] = df_symbol['P2Met']
    df_full_l['Total'] = df_symbol['Total']
    df_full_l['Total'] = df_symbol['Total']

    df_full.reset_index(drop=True, inplace=True)
    df_full_l.reset_index(drop=True, inplace=True)

    df = pd.concat( [df_full, df_full_l], axis=0)
    df.sort_values(by=['Symbol'], inplace=True)
    df.to_csv(path + outputfile, index=False)


def AnaylseResults(path, filename):
    fullDF = pd.read_csv(path + filename, index_col = 0)
    risk = 1
    # Set index to datetime to filter by year
    fullDF.index = pd.to_datetime(fullDF.index)

    times = ['09:30','10:30','12:30','15:30']
    orPercATR = [0, 0.25, 0.5, 1, 99999]
    VWAPDiff = [0, 2.5, 5, 10, 99999]

    # Date	Symbol	PreVolume	preMarketHigh	preMarketLow	OR	ATR	OR%ofATR	yHigh	yLow	VWAP	VWAP%DiffPrice	Entry	Stop	StopType	RiskPerShare	EntryTime	PB#	PT1	PT1-time	P1Met	PT2	PT2-time	P2Met	Figure

    columns=['Year','Time','LongShort','ORPerc','VWAPPerc','WithinPreRange','AbovePreH','BelowPreLow','WithinYRange','AboveYHigh','BelowYLow','Total','Wins','Losses','WinPerc','PT1','PT2','pnl','R:R','LossVal','WinVal','PT1Val','PT2Val','WinValPerc']
    rows = []
    year = [2019,2020,2021,2022]
    for n in year:
        # All
        loss = fullDF[(fullDF.P1Met == 0) & (fullDF.index.year == n)].shape[0]
        pt1Met = fullDF[(fullDF.P1Met == 1) & (fullDF.index.year == n)].shape[0]
        pt2Met = fullDF[(fullDF.P2Met == 1) & (fullDF.index.year == n)].shape[0]
        # Write to file
        rows.append(WriteLine(n,'All','All', 'All', 'All', 'All', 'All', 'All', 'All', 'All', 'All', loss, pt1Met, pt2Met, risk))

        direction  = ['Short','Long']
        for k in direction:
            # Filter
            df = fullDF[(fullDF.Type == k) & (fullDF.index.year == n)]

            # All
            loss = df[(df.P1Met == 0)].shape[0]
            pt1Met = df[(df.P1Met == 1)].shape[0]
            pt2Met = df[(df.P2Met == 1)].shape[0]
            # Write to file
            rows.append(WriteLine(n,'All',k, 'All', 'All', 'All', 'All', 'All', 'All', 'All', 'All', loss, pt1Met, pt2Met, risk))

            # All trades above pre high and yhigh
            loss = df[(df.P1Met == 0) & (df.Entry >= df.preMarketHigh) & (df.Entry >= df.yLow) & (df.Entry <= df.yHigh)].shape[0]
            pt1Met = df[(df.P1Met == 1) & (df.Entry >= df.preMarketHigh) & (df.Entry >= df.yLow) & (df.Entry <= df.yHigh)].shape[0]
            pt2Met = df[(df.P2Met == 1) & (df.Entry >= df.preMarketHigh) & (df.Entry >= df.yLow) & (df.Entry <= df.yHigh)].shape[0]
            # Write to file
            rows.append(WriteLine(n,'All',k, 'All', 'All', 0, 1, 0, 1, 0, 0, loss, pt1Met, pt2Met, risk))

            # All trades less than pre low and within yRange
            loss = df[(df.P1Met == 0) & (df.Entry <= df.preMarketLow)  & (df.Entry >= df.yLow) & (df.Entry <= df.yHigh)].shape[0]
            pt1Met = df[(df.P1Met == 1) & (df.Entry <= df.preMarketLow) & (df.Entry >= df.yLow) & (df.Entry <= df.yHigh)].shape[0]
            pt2Met = df[(df.P2Met == 1) & (df.Entry <= df.preMarketLow) & (df.Entry >= df.yLow) & (df.Entry <= df.yHigh)].shape[0]
            # Write to file
            rows.append(WriteLine(n,'All', k,'All', 'All', 0, 0, 1, 1, 0, 0, loss, pt1Met, pt2Met, risk))

            # All trades in pre range
            loss = df[(df.P1Met == 0) & (df.Entry >= df.preMarketLow) & (df.Entry <= df.preMarketHigh)].shape[0]
            pt1Met = df[(df.P1Met == 1) & (df.Entry >= df.preMarketLow) & (df.Entry <= df.preMarketHigh)].shape[0]
            pt2Met = df[(df.P2Met == 1) & (df.Entry >= df.preMarketLow) & (df.Entry <= df.preMarketHigh)].shape[0]
            # Write to file
            rows.append(WriteLine(n,'All',k, 'All', 'All', 1, 0, 0, 'All', 'All', 'All', loss, pt1Met, pt2Met, risk))

            # All trades above pre high
            loss = df[(df.P1Met == 0) & (df.Entry >= df.preMarketHigh)].shape[0]
            pt1Met = df[(df.P1Met == 1) & (df.Entry >= df.preMarketHigh)].shape[0]
            pt2Met = df[(df.P2Met == 1) & (df.Entry >= df.preMarketHigh)].shape[0]
            # Write to file
            rows.append(WriteLine(n,'All',k, 'All', 'All', 0, 1, 0, 'All', 'All', 'All', loss, pt1Met, pt2Met, risk))

            # All trades less than pre low
            loss = df[(df.P1Met == 0) & (df.Entry <= df.preMarketLow)].shape[0]
            pt1Met = df[(df.P1Met == 1) & (df.Entry <= df.preMarketLow)].shape[0]
            pt2Met = df[(df.P2Met == 1) & (df.Entry <= df.preMarketLow)].shape[0]
            # Write to file
            rows.append(WriteLine(n,'All', k,'All', 'All', 0, 0, 1, 'All', 'All', 'All', loss, pt1Met, pt2Met, risk))

            # All trades in yesterday range
            loss = df[(df.P1Met == 0) & (df.Entry >= df.yLow) & (df.Entry <= df.yHigh)].shape[0]
            pt1Met = df[(df.P1Met == 1) & (df.Entry >= df.yLow) & (df.Entry <= df.yHigh)].shape[0]
            pt2Met = df[(df.P2Met == 1) & (df.Entry >= df.yLow) & (df.Entry <= df.yHigh)].shape[0]
            # Write to file
            rows.append(WriteLine(n,'All',k, 'All', 'All', 'All', 'All', 'All', 1, 0, 0, loss, pt1Met, pt2Met, risk))

            # All trades above yesterday low
            loss = df[(df.P1Met == 0) & (df.Entry >= df.yHigh)].shape[0]
            pt1Met = df[(df.P1Met == 1) & (df.Entry >= df.yHigh)].shape[0]
            pt2Met = df[(df.P2Met == 1) & (df.Entry >= df.yHigh)].shape[0]
            # Write to file
            rows.append(WriteLine(n,'All',k, 'All', 'All','All', 'All', 'All', 0, 1, 0, loss, pt1Met, pt2Met, risk))

            # All trades less than yesterday low
            loss = df[(df.P1Met == 0) & (df.Entry <= df.yLow)].shape[0]
            pt1Met = df[(df.P1Met == 1) & (df.Entry <= df.yLow)].shape[0]
            pt2Met = df[(df.P2Met == 1) & (df.Entry <= df.yLow)].shape[0]
            # Write to file
            rows.append(WriteLine(n,'All', k,'All', 'All', 'All', 'All', 'All', 0, 0, 1, loss, pt1Met, pt2Met, risk))

            # Time filter
            for i in range(0, len(times)-1):
                loss = df[(df.P1Met == 0) & (df.EntryTime >= times[i]) & (df.EntryTime < times[i+1])].shape[0]
                pt1Met = df[(df.P1Met == 1) & (df.EntryTime >= times[i]) & (df.EntryTime < times[i+1])].shape[0]
                pt2Met = df[(df.P2Met == 1) & (df.EntryTime >= times[i]) & (df.EntryTime < times[i+1])].shape[0]
                # Write to file
                rows.append(WriteLine(n,times[i] + ' to ' + times[i+1], 'All', 'All','All', 'All', 'All', 'All', 'All', 'All', 'All', loss, pt1Met, pt2Met, risk))

            # OR Perc filter
            for i in range(1, len(orPercATR)):
                # With ATR %
                loss = df[(df.P1Met == 0) & (df['OR%ofATR'] >= orPercATR[i-1]) & (df['OR%ofATR'] < orPercATR[i])].shape[0]
                pt1Met = df[(df.P1Met == 1) & (df['OR%ofATR'] >= orPercATR[i-1]) & (df['OR%ofATR'] < orPercATR[i])].shape[0]
                pt2Met = df[(df.P2Met == 1) & (df['OR%ofATR'] >= orPercATR[i-1]) & (df['OR%ofATR'] < orPercATR[i])].shape[0]
                # Write to file
                rows.append(WriteLine(n,'All', k,'OR%ofATR ' + str(orPercATR[i-1]) + ' to ' + str(orPercATR[i]), 'All', 'All', 'All', 'All', 'All', 'All', 'All', loss, pt1Met, pt2Met, risk))

            # VWAP % filter
            for i in range(1, len(VWAPDiff)):
                # With VWAP %
                loss = df[(df.P1Met == 0) & (df['VWAP%DiffPrice'] >= VWAPDiff[i-1]) & (df['VWAP%DiffPrice'] < VWAPDiff[i])].shape[0]
                pt1Met = df[(df.P1Met == 1) & (df['VWAP%DiffPrice'] >= VWAPDiff[i-1]) & (df['VWAP%DiffPrice'] < VWAPDiff[i])].shape[0]
                pt2Met = df[(df.P2Met == 1) & (df['VWAP%DiffPrice'] >= VWAPDiff[i-1]) & (df['VWAP%DiffPrice'] < VWAPDiff[i])].shape[0]
                # Write to file
                rows.append(WriteLine(n,'All',k, 'All', 'VWAP%DiffPrice ' + str(VWAPDiff[i-1]) + ' to ' + str(VWAPDiff[i]), 'All', 'All', 'All', 'All', 'All', 'All', loss, pt1Met, pt2Met, risk))

    resultsDF = pd.DataFrame(rows, columns=columns)
    resultsDF.to_csv(path + filename.replace('Raw','Analysis'), index=False)

# hodBars is the number of bars before retesting HOD
# ORBars is the number of bars in the open range, the HOD/LOD must be outside of this
def Analyse(symbol, source, destination, hodBars, ORBars, marketOnly=True, outputFigures=False):
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

    # Remove extra slashes
    source = os.path.normpath(source + symbol)


    # Load DF (source, year, month, day)
    df = OpenFile(source, 2019, 1, 1)

    # Check index is correct format
    if type(df.index) != pd.core.indexes.datetimes.DatetimeIndex: return

    # Open 5 minute chart
    #currDir = os.path.basename(os.path.dirname(source))
    #fivePath = source.replace(currDir,"5m")
    #dfFive = OpenFile(fivePath)

    # Filter out symbols that are penny stocks or too high in value
    #if df.close.min() > 80 or df.close.max() < 5: return

    # Select pre-market data
    dfPreMarket = df[df.Market == 0]

    # Open market only
    df = df[df.Market != 2]
    #dfFive = dfFive[dfFive.Market == 1]

    # log file:
    fileName = str(hodBars) + 'PB_' + str(ORBars) + 'OR_Raw.csv'
    if not os.path.exists(destination + fileName):
        with open(destination + fileName, "w") as f:
            f.write("Date,Symbol,Type,PreVolume,preMarketHigh,preMarketLow,OR,ATR,OR%ofATR,yHigh,yLow,VWAP,VWAP%DiffPrice,Entry,Stop,StopType,RiskPerShare,EntryTime,PB#,PBBars,topWickPerc,bottomWickPerc,bodyUpPerc,bodyDownPerc,PT1,PT1-time,P1Met,PT2,PT2-time,P2Met,Figure\n")
    f = open(destination + fileName, 'a')
    """ Parameters """
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
        Date = day.index.time
        CandleDir = day.Candle.to_numpy()
        Close = day.close.to_numpy()
        Open = day.open.to_numpy()
        Vol = day.volume.to_numpy()
        VWAP = day.vwap.to_numpy()

        # Filter out symbols that are penny stocks or too high in value
        if min(Low) > 250 or max(High) < 5: continue

        # Create figure
        figure = Figure.Figure()
        figure.CandleStick(day)
        figure.TextConfig(chartTitle=f"{symbol} : {idx}")
        figure.AddLine(day, "vwap", "yellow", "VWAP",2)
        figure.AddLine(day, "50EMA", "blue", "50EMA",2)

        # Update high and low now that they have been used
        # This is ready for the next iteration
        yLow = min(day.low.to_numpy())
        yHigh = max(day.high.to_numpy())

        # Premarket data
        preMarket = dfPreMarket[dfPreMarket.index.date == idx]
        # Error checking
        if len(preMarket.index) == 0:
            continue
        # Premarket values
        preMarketHigh = max(preMarket.high)
        preMarketLow = min(preMarket.low)
        preMarketVol = sum(preMarket.volume.to_numpy())

        # Exclude low pre-market volume or low OR volume
        if preMarketVol < 500000 and sum(Vol[0:ORBars]) < 2000000:
            continue

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

        Up = 0
        Down = 0
        Even = 0

        UpVol = 0
        DownVol = 0
        EvenVol = 0

        ORType = ""


        # Variables
        currHigh = 0
        highIndex = 0
        currLow = 99999
        lowIndex = 0
        pbBarCount = 0
        topWickPerc = 0
        bottomWickPerc = 0
        bodyUpPerc = 0
        bodyDownPerc = 0
        # 15 min ORB
        orbHigh = max(High[0:ORBars])
        orbLow = min(Low[0:ORBars])
        orbRange = round(orbHigh-orbLow,2)
        orbPerc = round(orbRange / ATR,4)
        #figure.AddStopLine(Date[0], Date[len(Date)-1], orbHigh, "H")
        #figure.AddStopLine(Date[0], Date[len(Date)-1], orbLow, "L")
        # Variable reset
        reset = False
        # Entry counter
        entries = 0
        entryTime = ""
        entryVwap = 0
        # Figure destination
        fileLocation = destination + "/figures/" + symbol + "_" + str(idx) + ".png"
        # Iterate through the candlesticks of the current day
        for i in range(0, len(Low)):
            rangeBar = abs(High[i] - Low[i])
            # Calculate percent
            if rangeBar > 0:
                # Calculate size of body
                bodyPerc = abs(Close[i] - Open[i]) / rangeBar
                # If red bar
                if CandleDir[i] == -1:
                    topWick = High[i] - Open[i]
                    bottomWick = Close[i] - Low[i]
                    bodyDownPerc += bodyPerc
                else:
                    topWick = High[i] - Close[i]
                    bottomWick = Open[i] - Low[i]
                    bodyUpPerc += bodyPerc

                # Calculate top and bottom wick
                topWickPerc += topWick / rangeBar
                bottomWickPerc += bottomWick / rangeBar


            # Do not trade within first 15 minutes
            if i < ORBars:
                # Get the current high and low
                if currHigh < High[i]:
                    currHigh = High[i]
                    highIndex = i
                if currLow > Low[i]:
                    currLow = Low[i]
                    lowIndex = i
                continue

            if not breakAbove and not breakBelow and str(Date[i]) <= '10:15:00' and str(Date[i]) >= '09:35:00': #and Date[i] > '09:44:00':
                # Look for break above HOD: check high is above current high, that the bar opens above VWAP and that it was at least 1 bar ago (a pullback)
                if(High[i] > currHigh and Open[i] > VWAP[i] and highIndex+hodBars < i and High[i] > orbHigh and currHigh > preMarketHigh):
                    ####
                    #### L O N G   E N T R Y
                    ####
                    entryPrice = currHigh + 0.01
                    #stopLoss = Low[i] - 0.01
                    #stopLoss = round(entryPrice - (ATR / 4),2)
                    stopLoss = min(Low[highIndex:i])
                    riskPerShare = round((entryPrice - stopLoss),2)

                    # Don't risk under 0.05 and Don't risk more than $0.35
                    if riskPerShare < 0.05:
                        break

                    # Set targets
                    profitOne = round((riskPerShare * 2.0) + entryPrice,2)
                    profitTwo = round((riskPerShare * 3.0) + entryPrice,2)

                    # number of bars in PB
                    pbBarCount = i - highIndex

                    # Add to figure
                    figure.AddMarker(Date[i], entryPrice, 'triangle-up', 'green', "(L)", size=16)
                    #entries = entries + 1
                    entryTime = Date[i].strftime("%H:%M")
                    entryVwap = VWAP[i]
                    tradeType = 'Long'
                    breakAbove = True
                    drawFigure = True

                elif(Low[i] < currLow and Open[i] < VWAP[i] and lowIndex+hodBars < i and Low[i] < orbLow and currLow < preMarketLow):
                    ####
                    #### S H O R T    E N T R Y
                    ####
                    entryPrice = currLow - 0.01
                    #stopLoss = High[i] + 0.01
                    #stopLoss = round(entryPrice + (ATR / 4),2)
                    stopLoss = min(High[lowIndex:i])
                    riskPerShare = round((stopLoss - entryPrice),2)

                    # Don't risk under 0.05 and Don't risk more than $0.35
                    if riskPerShare < 0.05:
                        break

                    # Set targets
                    profitOne = round(entryPrice - (riskPerShare * 2.0) ,2)
                    profitTwo = round(entryPrice - (riskPerShare * 3.0) ,2)

                    # number of bars in PB
                    pbBarCount = i - lowIndex

                    # Add to figure
                    figure.AddMarker(Date[i], entryPrice, 'triangle-down', 'red', "(S)", size=16)
                    entries = entries + 1
                    entryTime = Date[i].strftime("%H:%M")
                    entryVwap = VWAP[i]
                    tradeType = 'Short'
                    breakBelow = True
                    drawFigure = True

            # L O N G
            elif breakAbove:
                # P R O F I T   O N E
                if(High[i] >= profitOne and not profitOneMet):
                    # profit target met
                    profitOneMet = True
                    P1Met = 1
                    profitOneTime = Date[i].strftime("%H:%M")
                    # Add exit to figure
                    figure.AddMarker(Date[i], profitOne, 'triangle-down', 'blue', "(PT1)", size=16)

                # P R O F I T   T W O
                elif(High[i] >= profitTwo):
                    # profit target met
                    P2Met = 1
                    profitTwoTime = Date[i].strftime("%H:%M")
                    # Write
                    f.write(f"{idx},{symbol},{tradeType},{preMarketVol},{preMarketHigh},{preMarketLow},{orbRange},{ATR},{orbPerc},{yHigh},{yLow},{entryVwap}, {abs(round((1 - (entryPrice/entryVwap)) * 100,2))},{entryPrice},{stopLoss},{stopType},{riskPerShare},{entryTime},{entries},{pbBarCount},{round(topWickPerc/i,3)},{round(bottomWickPerc/i,3)},{round(bodyUpPerc/i,3)},{round(bodyDownPerc/i,3)},{profitOne},{profitOneTime}, {P1Met},{profitTwo},{profitTwoTime},{P2Met},{fileLocation}\n")
                    # Add exit to figure
                    figure.AddMarker(Date[i], profitTwo, 'triangle-down', 'blue', "(PT2)", size=16)
                    # Reset variables
                    reset = True

                # S T O P
                elif(Low[i] < stopLoss and not reset):
                    # Lost trade
                    stoppedOut = True
                    profitOneMet = False
                    # Write
                    f.write(f"{idx},{symbol},{tradeType},{preMarketVol},{preMarketHigh},{preMarketLow},{orbRange},{ATR},{orbPerc},{yHigh},{yLow},{entryVwap}, {abs(round((1 - (entryPrice/entryVwap)) * 100,2))},{entryPrice},{stopLoss},{stopType},{riskPerShare},{entryTime},{entries},{pbBarCount},{round(topWickPerc/i,3)},{round(bottomWickPerc/i,3)},{round(bodyUpPerc/i,3)},{round(bodyDownPerc/i,3)},{profitOne},{profitOneTime},{P1Met},{profitTwo},{profitTwoTime},{P2Met},{fileLocation}\n")
                    # Add exit to figure
                    figure.AddMarker(Date[i], stopLoss, 'triangle-down', 'red', '(SL)', size=16)
                    # Reset variables
                    reset = True
            # S H O R T
            elif breakBelow:
                # P R O F I T   O N E
                if(Low[i] <= profitOne and not profitOneMet):
                    # profit target met
                    profitOneMet = True
                    P1Met = 1
                    profitOneTime = Date[i].strftime("%H:%M")
                    # Add exit to figure
                    figure.AddMarker(Date[i], profitOne, 'triangle-down', 'blue', "(PT1)" , size=16)

                # P R O F I T   T W O
                elif(Low[i] <= profitTwo):
                    # profit target met
                    P2Met = 1
                    profitTwoTime = Date[i].strftime("%H:%M")
                    # Write
                    f.write(f"{idx},{symbol},{tradeType},{preMarketVol},{preMarketHigh},{preMarketLow},{orbRange},{ATR},{orbPerc},{yHigh},{yLow},{entryVwap}, {abs(round((1 - (entryPrice/entryVwap)) * 100,2))},{entryPrice},{stopLoss},{stopType},{riskPerShare},{entryTime},{entries},{pbBarCount},{round(topWickPerc/i,3)},{round(bottomWickPerc/i,3)},{round(bodyUpPerc/i,3)},{round(bodyDownPerc/i,3)},{profitOne},{profitOneTime},{P1Met},{profitTwo},{profitTwoTime},{P2Met},{fileLocation}\n")
                    # Add exit to figure
                    figure.AddMarker(Date[i], profitTwo, 'triangle-down', 'blue', "(PT2)", size=16)
                    # Reset variables
                    reset = True

                # S T O P
                elif(High[i] > stopLoss and not reset):
                    # Lost trade
                    stoppedOut = True
                    # Write
                    f.write(f"{idx},{symbol},{tradeType},{preMarketVol},{preMarketHigh},{preMarketLow},{orbRange},{ATR},{orbPerc},{yHigh},{yLow},{entryVwap}, {abs(round((1 - (entryPrice/entryVwap)) * 100,2))},{entryPrice},{stopLoss},{stopType},{riskPerShare},{entryTime},{entries},{pbBarCount},{round(topWickPerc/i,3)},{round(bottomWickPerc/i,3)},{round(bodyUpPerc/i,3)},{round(bodyDownPerc/i,3)},{profitOne},{profitOneTime},{P1Met},{profitTwo},{profitTwoTime},{P2Met},{fileLocation}\n")
                    # Add exit to figure
                    figure.AddMarker(Date[i], stopLoss, 'triangle-up', 'green', '(SL)', size=16)
                    # Reset variables
                    reset = True

            # Reset all variables to default after a stop out or when profit target two is reached
            if reset:
                # Reset variables
                breakBelow = False
                breakAbove = False
                profitOneMet = False
                P1Met = 0
                P2Met = 0
                profitTwoTime = ""
                profitOneTime = ""
                entryVwap = 0
                tradeType = None
                pbBarCount = 0
                # default
                reset = False

            # Get the current high and low
            if currHigh < High[i]:
                currHigh = High[i]
                highIndex = i
            if currLow > Low[i]:
                currLow = Low[i]
                lowIndex = i

        if drawFigure and outputFigures:
            figure.Save(fileLocation)
