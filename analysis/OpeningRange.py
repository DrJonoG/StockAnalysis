
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

# analysis of the impact of the previous day close, to the current day based on the opening bar

import os
import re
import time
import datetime
import numpy as np
import pandas as pd
from core import Figure
from pathlib import Path
from helpers import csvToPandas, PrintProgressBar

"""
=> Opening Price looks at how to intial opening range dictates the rest of the day
=>
"""

def Analyse(symbol, source, destination, openingRange=3, marketOnly=True):
    """
    A function to calculate opening range

    Parameters
    ----------
    df : Dataframe
        A dataframe for a single symbol
    source : String
        The location of the symbol csv files
    destination : String
        Path to where to save the analysis
    openingRange : Int
        The number of bars, in your chosen time frame, that defines the opening range
    marketOnly : Bool
        A boolean to use only market opening hours (if true) or all times (if false)
    """
    # Load DF
    df = csvToPandas(source + symbol)

    # OR is the opening range, C is close, O is open, yC is yesterdays close -> denotes the difference between left and right
    # log file:
    fileName = symbol[0] + '_Summary.csv'
    if not os.path.exists(destination + fileName):
        with open(destination + fileName, "w") as f:
            f.write("Symbol,Datetime,yC,O,% yC->O,$ yC->O,OR High,OR Low,OR ATR,ATR,OR%ofATR,OR %,OR Break Above/Below/None,Reverse back to OR,Full OR breakout reversal,Close in ORB Direction?,Close in opposite ORB dir,% OR L->Day Low,% OR H->Day High,Day Low,Day High,C,Volume\n")

    # Empty dictionary list for storage
    dictList = list()
    # Group on date intraday analysis
    groupedDF = df.groupby(df.index.date, group_keys=False)
    # Number of days
    totalDays = groupedDF.ngroups
    # Convert to list
    groupedDF = list(groupedDF)
    # Iterate through groups, skip first two groups for lookback
    with open(destination + fileName, "a") as f:
        for index in range(14, len(groupedDF)):
            # Get the days
            currDay = groupedDF[index][1]
            yDay = groupedDF[index-1][1]
            # Calculate atr:
            atrArr = []
            for i in range(index-14, index):
                currDay = groupedDF[index][1]
                atr = currDay.high - currDay.low
                atrArr = np.append(atrArr, atr)
            dailyATR = round(np.mean(atrArr),2)
            # Daily ATR has to be at least $0.30
            if dailyATR < 0.25:
                continue
            # Pre market
            preMarket = currDay[currDay.Market == 0]
            preMarketVol = preMarket['volume'].sum()
            # Skip if volume for premarket is too low
            if preMarketVol < 200000:
                continue;
            # If only looking at open data, filter out the rest
            if marketOnly:
                currDay = currDay[currDay.Market == 1]
                yDay = yDay[yDay.Market == 1]

            # Check for data
            # We check for 2 as we need a start and end value
            if len(currDay) < 2 or len(yDay) < 2:
                return

            yClose = yDay.iloc[-1].close
            firstBarOpen = currDay.iloc[0].open
            # Comparison to yesterdays data
            change = firstBarOpen - yClose
            gap = round((change / yClose), 5)
            # The high and low of the opening range
            ORLow = min(currDay[0:openingRange].low)
            ORHigh = max(currDay[0:openingRange].high)
            # Check populated
            if ORLow == 0 or ORHigh == 0:
                return
            # Define OR
            OR = ORHigh - ORLow
            # Assignment
            data = f"{symbol},{currDay.index[0].strftime('%Y-%m-%d')},{yClose},{firstBarOpen},{gap},{change},{ORHigh},{ORLow},{OR},{dailyATR},{round(OR/dailyATR,2)},{round((OR/ORLow),5)}"
            # The change in the current day from start to end (not just one bar, but whole day)
            lastBarClose = currDay.iloc[-1].close
            dayChange = round(((lastBarClose - firstBarOpen) / firstBarOpen), 5)
            # check if data exists
            if len(currDay[openingRange:]) == 0:
                return
            # Remaining data
            dayLow = min(currDay[openingRange:].low)
            dayHigh = max(currDay[openingRange:].high)
            # Check for valid values
            if dayLow <= 0 or dayHigh <= 0:
                return
            # Create figure
            figure = Figure.Figure()
            figure.CandleStick(pd.concat((yDay,currDay)))
            figure.TextConfig(chartTitle=f"{symbol}. Date {currDay.index[0]}... Premarket Volume: {str(preMarketVol)}... ATR {str(dailyATR)}")
            figure.AddStopLine(currDay.index[0], currDay.index[len(currDay)-1], ORLow, "OR Low")
            figure.AddStopLine(currDay.index[0], currDay.index[len(currDay)-1], ORHigh, "OR High")
            # Does the close break the opening range
            # Above is represented by 1, below is -1 and within OR is 0
            breakType = 0
            reverseToOR = False
            completeReverse = False
            closeInORBDirection = False
            closeInOppDirection = False
            for position, closeIter in enumerate(currDay[openingRange:].close):
                if closeIter > ORHigh:
                    breakType = 1
                    # Check if the OR break reverses back to OR or completely reverses
                    for subTime in currDay[openingRange + position:].close:
                        if subTime < ORHigh:
                            reverseToOR = True
                        if subTime < ORLow:
                            completeReverse = True
                    # Is the close in the same direction as the breakout
                    if currDay.iloc[-1].close >= ORHigh:
                        closeInORBDirection = True
                    elif currDay.iloc[-1].close <= ORLow:
                        closeInOppDirection = True
                    break

                if closeIter < ORLow:
                    breakType = -1
                    # Check if the OR break reverses back to OR or completely reverses
                    for subTime in currDay[openingRange + position:].close:
                        if subTime > ORLow:
                            reverseToOR = True
                        if subTime > ORHigh:
                            completeReverse = True
                    # Is the close in the same direction as the breakout
                    if currDay.iloc[-1].close <= ORLow:
                        closeInORBDirection = True
                    elif currDay.iloc[-1].close >= ORHigh:
                        closeInOppDirection = True
                    break

            # Assign the break type

            # Did breakout reverse back to OR
            # Did breakout completely reverse to opposite side
            # Did symbol close in the direction of the breakout
            # The percentage difference between the OR low and the day low
            # The percentage difference between the OR high and the day high
            # Current day low
            # Current day high
            # The close
            # Volume
            data = data + f",{breakType},{reverseToOR},{completeReverse},{closeInORBDirection},{closeInOppDirection},{round((ORLow - dayLow)/dayLow,5)},{round((ORHigh - dayHigh)/dayHigh,5)},{dayLow},{dayHigh},{currDay.iloc[-1].close},{sum(currDay.volume)}\n"
            f.write(data)
            # Write figure
            fileLocation = destination + "/figures/" + symbol + "_" + str(index) + ".png"
            figure.Save(fileLocation)

def Summary(directory, destination):
    # Load all files
    if not os.path.exists(directory + 'Merged.csv'):
        files = list(Path(directory).rglob('*.csv'))
        masterDF = pd.concat((pd.read_csv(f, header = 0) for f in files))
        masterDF.to_csv(directory + 'Merged.csv', index=False)
    else:
        # Load master
        masterDF = pd.read_csv(directory + 'Merged.csv', index_col = 0)

    # Filters
    masterDF = masterDF[((masterDF['yC'] > 0.5) & (masterDF['yC'] < 250))]
    masterDF = masterDF[(masterDF['Volume'] > 500000)]
    masterDF['OR %'] = masterDF['OR %'] * 100
    masterDF= masterDF[masterDF['OR %'] < 60]

    # Groups
    masterDF['priceGroup'] = pd.cut(masterDF['yC'], 25)
    masterDF['ORPercent'] = pd.cut(masterDF['OR %'], 60)

    # Analysis by price
    groupedDF = masterDF.groupby(masterDF['priceGroup'], group_keys=False)
    with open(destination + 'ORB_GrpByPrice.csv', 'w') as f:
        header = "Price Range,Total Days,OR % of Price,ORB Above,ORB Below,ORB None,Reverse to OR,Full OR Reversal,Close in ORB Direction,Close in Opp Dir,Close between OR\n"
        f.write(header)
        for name, group in groupedDF:
            line = AnalyseGroups(group, name)
            f.write(line)

    # Analysis of both OR percent and price grouped
    with open(destination + 'ORB_GrpByORPercentPrice.csv', 'w') as f:
        header = "Price Range,OR Percent,Total Days,OR % of Price,ORB Above,ORB Below,ORB None,Reverse to OR,Full OR Reversal,Close in ORB Direction,Close in Opp Dir,Close between OR\n"
        f.write(header)
        for priceName, priceGroup in groupedDF:
            groupedDFSub = priceGroup.groupby(priceGroup['ORPercent'], group_keys=False)
            for name, group in groupedDFSub:
                line = AnalyseGroups(group, name)
                priceName = re.sub('[\(\]]', '', str(priceName)).replace(","," to ")
                f.write(f"{priceName},"+line)

    # Analysis by OR percentage of price
    groupedDF = masterDF.groupby(masterDF['ORPercent'], group_keys=False)
    with open(destination + 'ORB_GrpByORPercent.csv', 'w') as f:
        header = "OR Percent,Total Days,OR % of Price,ORB Above,ORB Below,ORB None,Reverse to OR,Full OR Reversal,Close in ORB Direction,Close in Opp Dir,Close between OR\n"
        f.write(header)
        for name, group in groupedDF:
            line = AnalyseGroups(group, name)
            f.write(line)

def AnalyseGroups(group, name):
    ORPercent = round(group['OR %'].mean(),2)
    ORBreak = group['OR Break Above/Below/None'].value_counts()
    ORReverse = group['Reverse back to OR'].value_counts()
    ORFullReverse = group['Full OR breakout reversal'].value_counts()
    ORCloseDirection = group['Close in ORB Direction?'].value_counts()
    ORCloseOppDirection = group['Close in opposite ORB dir'].value_counts()

    # Total Days
    totalOR = ORBreak.sum()
    # Calculate percentages of breakouts
    ORBBelow = 0
    ORBAbove = 0
    ORBNone = 0
    if 1 in ORBreak: ORBAbove = round(1 - (totalOR - ORBreak[1]) / totalOR,2)
    if -1 in ORBreak: ORBBelow = round(1 - (totalOR - ORBreak[-1]) / totalOR,2)
    if 0 in ORBreak: ORBNone = round(1 - (totalOR - ORBreak[0]) / totalOR,2)
    # Calculate percent that return to OR
    ORBRevTrue = 0
    if 1 in ORReverse: ORBRevTrue = round(1 - (totalOR - ORReverse[1]) / totalOR,2)
    # Calculate percent that completely reverses
    ORBFullRev = 0
    if 1 in ORFullReverse: ORBFullRev = round(1 - (totalOR - ORFullReverse[1]) / totalOR,2)
    # Calculate percent that close in initial ORB direction
    ORBCloseDir = 0
    if 1 in ORCloseDirection: ORBCloseDir = round(1 - (totalOR - ORCloseDirection[1]) / totalOR,2)
    # Calculate percent that close in opposite ORB direction
    ORBOppCloseDir = 0
    if 1 in ORCloseOppDirection: ORBOppCloseDir = round(1 - (totalOR - ORCloseOppDirection[1]) / totalOR,2)
    # Write line
    name = re.sub('[\(\]]', '', str(name)).replace(","," to ")
    line = f"{name},{totalOR},{ORPercent},{ORBAbove},{ORBBelow},{ORBNone},{ORBRevTrue},{ORBFullRev},{ORBCloseDir},{ORBOppCloseDir},{round(1-(ORBOppCloseDir+ORBCloseDir),2)}\n"
    return line
