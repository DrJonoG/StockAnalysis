
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
=> Gappers looks at how the gap between open and close impacts the remainder of the day.
=> Does a large gap up result in a closure of the gap in the day?
=> If so, typically when is this gap closed and what happens next
"""

def Analyse(symbol, source, destination, marketOnly=True):
    """
    A function to calculate opening range, gaps, and the changes throughout the day

    Parameters
    ----------
    symbol : String
        The filename of the csv file to analyse
    source : String
        The location of the symbol csv files
    destination : String
        Path to where to save the analysis
    marketOnly : Bool
        A boolean to use only market opening hours (if true) or all times (if false)
    """
    # log file:
    fileName = symbol[0] + '_Summary.csv'
    if not os.path.exists(destination + fileName):
        with open(destination + fileName, "w") as f:
            f.write("Symbol,Datetime,yOpen,yClose,yChange (%),yChange($),yClose RSI,Day Open,Gap (%),Gap ($),ATR,ATR%ofGap,Gap Filled,Gap Reached,Gap Filled after 10am,Gap reached after 10am,Day High,Day Low,Day Close,Day Change,Volume,PreVolume\n")
    # Load DF
    df = csvToPandas(source + symbol)
    # Group on date intraday analysis
    groupedDF = df.groupby(df.index.date, group_keys=False)
    # Daily statistics
    dailyStats = groupedDF.close.agg(['max', 'min', 'count', 'median', 'mean'])
    # Convert to list
    groupedDF = list(groupedDF)
    # Iterate through groups, skip first two groups for lookback
    with open(destination + fileName, "a") as f:


        for index in range(14, len(groupedDF)):
            try:
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
                # Get the days
                currDay = groupedDF[index][1]
                yDay = groupedDF[index-1][1]
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
                # Check if days exist
                if (len(yDay.index) < 1 or len(currDay.index) < 1):
                    continue
                # The change in the previous day between open and close
                yClose = yDay.iloc[-1].close
                yOpen = yDay.iloc[0].open
                # Ensure data is available
                if (yOpen == 0 or yClose == 0):
                    continue
                # Calculate change in yesterdays market
                yChange = round(((yClose - yOpen) / yOpen), 5)
                # The gap between yesterday day close and market open
                firstBarOpen = currDay.iloc[0].open
                gap = round(((firstBarOpen - yClose) / yClose), 5) # Change between yesterdays close and todays open, the gap.
                lastBarClose = currDay.iloc[-1].close
                dayChange = round(((lastBarClose - firstBarOpen) / firstBarOpen), 5)
                # If no change then no gap
                if gap == 0:
                    continue
                # Create figure
                figure = Figure.Figure()
                figure.CandleStick(pd.concat((yDay,currDay)))
                figure.TextConfig(chartTitle=f"{symbol}. Date {currDay.index[0]}... Premarket Volume: {str(preMarketVol)}... ATR {str(dailyATR)}")
                figure.AddStopLine(currDay.index[0], currDay.index[len(currDay)-1], firstBarOpen, "Market Open")
                figure.AddStopLine(currDay.index[0], currDay.index[len(currDay)-1], yClose, "Yesterday Close")
                figure.AddStopLine(currDay.index[0], currDay.index[len(currDay)-1], (firstBarOpen+yClose) / 2, "MidLine. Gapping " + str(gap*100)  + "%")
                # Gap direction
                if gap >= 0.01:
                    # Assignment
                    # Check if gap has been filled and what time
                    # This is whether the gap has been completely filled
                    gapFill = currDay[currDay.low < yClose].head(1)
                    gapFilled = "No"
                    if not gapFill.empty:
                        gapFilled = gapFill.index[0].strftime('%H:%M')

                    # Check if gap has been reached and what time:
                    # This is whether the price touched the gap
                    currDayRemainder = currDay[1:] # We exclude the first bar (the gap) as in theory this will always be touched
                    gapTouched = currDayRemainder[currDayRemainder.low < firstBarOpen].head(1)
                    touched = "No"
                    if not gapTouched.empty:
                        touched = gapTouched.index[0].strftime('%H:%M')

                    # Assignment
                    # Check if gap has been filled and what time after 10am
                    # This is whether the gap has been completely filled
                    gapFill = currDay[((currDay.low < yClose) & (currDay.index.hour >= 10))].head(1)
                    gapFilledLater = "No"
                    if not gapFill.empty:
                        gapFilledLater = gapFill.index[0].strftime('%H:%M')

                    # Check if gap has been reached and what time after 10am:
                    # This is whether the price touched the gap
                    gapTouched = currDay[((currDay.low < firstBarOpen) & (currDay.index.hour >= 10))].head(1)
                    touchedLater = "No"
                    if not gapTouched.empty:
                        touchedLater = gapTouched.index[0].strftime('%H:%M')
                elif gap <= -0.01:
                    # Assignment
                    # Check if gap has been filled and what time
                    # This is whether the gap has been completely filled
                    gapFill = currDay[currDay.high > yClose].head(1)
                    gapFilled = "No"
                    if not gapFill.empty:
                        gapFilled = gapFill.index[0].strftime('%H:%M')

                    # Check if gap has been reached and what time:
                    # This is whether the price touched the gap
                    currDayRemainder = currDay[1:] # We exclude the first bar (the gap) as in theory this will always be touched
                    gapTouched = currDayRemainder[currDayRemainder.high > firstBarOpen].head(1)
                    touched = "No"
                    if not gapTouched.empty:
                        touched = gapTouched.index[0].strftime('%H:%M')

                    # Assignment
                    # Check if gap has been filled and what time after 10am
                    # This is whether the gap has been completely filled
                    gapFill = currDay[((currDay.high > yClose) & (currDay.index.hour >= 10))].head(1)
                    gapFilledLater = "No"
                    if not gapFill.empty:
                        gapFilledLater = gapFill.index[0].strftime('%H:%M')

                    # Check if gap has been reached and what time after 10am:
                    # This is whether the price touched the gap
                    gapTouched = currDay[((currDay.high > firstBarOpen) & (currDay.index.hour >= 10))].head(1)
                    touchedLater = "No"
                    if not gapTouched.empty:
                        touchedLater = gapTouched.index[0].strftime('%H:%M')

                if gap <= -0.01 or gap >= 0.01:
                    # High and lows of the day
                    dayHigh = max(currDay.high)
                    dayLow = min(currDay.low)
                    # The clsoe and entire day change
                    dayClose = lastBarClose
                    dayChange = dayChange
                    dayVol = sum(currDay.volume)
                    # Assignment for CSV file
                    line = f"{symbol},{currDay.index[0].strftime('%Y-%m-%d')},{yOpen},{yClose},{yChange},{(yClose - yOpen)},{yDay.iloc[-1].RSI14},{firstBarOpen},{gap},{gap},{dailyATR},{round(dailyATR/gap,4)},{gapFilled},{touched},{gapFilledLater},{touchedLater},{dayHigh},{dayLow},{dayClose},{dayChange},{dayVol},{preMarketVol}\n"
                    f.write(line)
                    # Write figure
                    fileLocation = destination + "/figures/" + symbol + "_" + str(index) + ".png"
                    figure.Save(fileLocation)
            except Exception as e:
                print('Failed to do something: ' + str(e))
                print(f"\n ==> Error processing {symbol}\n")
                continue

def PercentageCalculation(group, column):
    # % of days that fill the gap before 10am
    gapCounts = group[column].value_counts()
    sumCounts = sum(gapCounts)
    gapFilledPerc = 1
    if 'No' in gapCounts:
        gapFilledPerc = round((sumCounts - gapCounts['No']) / sumCounts, 2)
    # Most common fill time
    mostCommonString = ''
    mostCommon = gapCounts.nlargest(n=4).index.values
    if len(mostCommon) < 4: rangeValue = len(mostCommon)
    else: rangeValue = 4
    for i in range(0,rangeValue):
        mostCommonString = mostCommonString + str(mostCommon[i]) + '->' + str(round(1-(sumCounts - gapCounts[mostCommon[i]]) / sumCounts,2)) + " "

    return (gapFilledPerc, mostCommonString)

def CalculateSummary(group, name):
    numRows = len(group.index)
    if numRows == 0: return

    gapFilledPerc, mostCommonString = PercentageCalculation(group, 'Gap Filled')
    gapFilledPercAfter, mostCommonStringAfter = PercentageCalculation(group, 'Gap Filled after 10am')
    gapReachedPerc, commonReachedString = PercentageCalculation(group, 'Gap Reached')
    gapReachedPercAfter, commonReachedStringAfter = PercentageCalculation(group, 'Gap reached after 10am')

    closeInDirection = round((len(group[(group['Gap ($)'] >= 0.0) & (group['Day Close'] > group['Day Open'])]) + # Positive
                        len(group[(group['Gap ($)'] < 0.0) & (group['Day Close'] < group['Day Open'])])) / numRows,2)  # Negative
    closeOppDirection = round((len(group[(group['Gap ($)'] >= 0.0) & (group['Day Close'] < group['yClose'])]) +
                        len(group[(group['Gap ($)'] < 0.0) & (group['Day Close'] > group['yClose'])])) / numRows,2)
    closeInGap = round(1-(closeInDirection + closeOppDirection),2)

    name = re.sub('[\(\]]', '', str(name)).replace(","," to ")
    line = f"{name},{numRows},{gapFilledPerc},{mostCommonString},{gapFilledPercAfter},{mostCommonStringAfter},{gapReachedPerc},{commonReachedString},{gapReachedPercAfter},{commonReachedStringAfter},{closeInDirection},{closeOppDirection},{closeInGap}\n"
    return line

def Summary(directory, destination):
    # Load all files
    if not os.path.exists(directory + 'Merged.csv'):
        files = list(Path(directory).rglob('*.csv'))
        masterDF = pd.concat((pd.read_csv(f, header = 0) for f in files))
        masterDF.to_csv(directory + 'Merged.csv', index=False)
    else:
        # Load master
        masterDF = pd.read_csv(directory + 'Merged.csv', index_col = 0)

    # Filter out very large and very small stocks and low volume
    masterDF = masterDF[((masterDF['yClose'] > 0.5) & (masterDF['yClose'] < 250))]
    masterDF = masterDF[((masterDF['Gap ($)'] > -15) & (masterDF['Gap ($)'] < 15))]
    masterDF = masterDF[((masterDF['yChange($)'] > -15) & (masterDF['yChange($)'] < 15))]
    masterDF = masterDF[(masterDF['Volume'] > 500000)]

    # Cut data
    masterDF['priceGroup'] = pd.cut(masterDF['Gap ($)'], 60)
    masterDF['closingPrice'] = pd.cut(masterDF['yOpen'], 100)
    masterDF['pricePercent'] = pd.cut(masterDF['Gap (%)'], 60)
    masterDF['yChangePercent'] = pd.cut(masterDF['yChange (%)'], 60)

    # Analysis by gap $
    groupedDF = masterDF.groupby(masterDF['priceGroup'], group_keys=False)
    with open(destination + 'GAP_GrpByGapPrice.csv', 'w') as f:
        header = "Gap $,# Days,% Filled before 10am,MostCommonFillTimes before 10am,% Filled after 10am,MostCommonFillTimes after 10am,% Reached before 10am,AvgReachTime before 10am,% Reached after 10am,AvgReachTime after 10am,% Close in Gap Dir,% Close opposite Gap dir,Close In Gap\n"
        f.write(header)
        for name, group in groupedDF:
            line = CalculateSummary(group, name)
            if line is not None:
                f.write(line)

    # Analysis by gap %
    groupedDF = masterDF.groupby(masterDF['pricePercent'], group_keys=False)
    with open(destination + 'GAP_GrpByGapPercent.csv', 'w') as f:
        header = "Gap %,# Days,% Filled before 10am,MostCommonFillTimes before 10am,% Filled after 10am,MostCommonFillTimes after 10am,% Reached before 10am,AvgReachTime before 10am,% Reached after 10am,AvgReachTime after 10am,% Close in Gap Dir,% Close opposite Gap dir,Close In Gap\n"
        f.write(header)
        for name, group in groupedDF:
            line = CalculateSummary(group, name)
            if line is not None:
                f.write(line)

    # Analysis by change yesterday
    groupedDF = masterDF.groupby(masterDF['yChangePercent'], group_keys=False)
    with open(destination + 'GAP_GrpByYChange.csv', 'w') as f:
        header = "yChange,# Days,% Filled before 10am,MostCommonFillTimes before 10am,% Filled after 10am,MostCommonFillTimes after 10am,% Reached before 10am,AvgReachTime before 10am,% Reached after 10am,AvgReachTime after 10am,% Close in Gap Dir,% Close opposite Gap dir,Close In Gap\n"
        f.write(header)
        for name, group in groupedDF:
            line = CalculateSummary(group, name)
            if line is not None:
                f.write(line)

    # Analysis by symbol price
    groupedDF = masterDF.groupby(masterDF['closingPrice'], group_keys=False)
    with open(destination + 'GAP_GrpByPrice.csv', 'w') as f:
        header = "Price,# Days,% Filled before 10am,MostCommonFillTimes before 10am,% Filled after 10am,MostCommonFillTimes after 10am,% Reached before 10am,AvgReachTime before 10am,% Reached after 10am,AvgReachTime after 10am,% Close in Gap Dir,% Close opposite Gap dir,Close In Gap\n"
        f.write(header)
        for name, group in groupedDF:
            line = CalculateSummary(group, name)
            if line is not None:
                f.write(line)
