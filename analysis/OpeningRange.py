
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
import time
import datetime
import pandas as pd
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
    openingRange : Int
        The number of bars, in your chosen time frame, that defines the opening range
    marketOnly : Bool
        A boolean to use only market opening hours (if true) or all times (if false)
    """
    # Load DF
    df = csvToPandas(source + symbol)

    # OR is the opening range, C is close, O is open, yC is yesterdays close -> denotes the difference between left and right
    columns = ['Datetime', 'yC', 'O', '% yC->O', '$ yC->O', 'OR High', 'OR Low', 'OR ATR', 'OR %']
    # Empty dictionary list for storage
    dictList = list()
    # Group on date intraday analysis
    groupedDF = df.groupby(df.index.date, group_keys=False)
    # Number of days
    totalDays = groupedDF.ngroups
    # Convert to list
    groupedDF = list(groupedDF)
    # Iterate through groups, skip first two groups for lookback
    for index in range(2, len(groupedDF)):
        # Get the days
        currDay = groupedDF[index][1]
        yDay = groupedDF[index-1][1]
        # If only looking at open data, filter out the rest
        if marketOnly:
            currDay = currDay[currDay.Market == 1]
            yDay = yDay[yDay.Market == 1]

        yClose = yDay.iloc[-1].close
        firstBarOpen = currDay.iloc[0].open
        # Comparison to yesterdays data
        change = firstBarOpen - yClose
        gap = round((change / yClose), 5)
        # The high and low of the opening range
        ORLow = min(currDay[0:openingRange].low)
        ORHigh = max(currDay[0:openingRange].high)
        OR = ORHigh - ORLow
        # Assignment
        data = [currDay.index[0].strftime('%Y-%m-%d'), yClose, firstBarOpen, gap, change, ORHigh, ORLow, OR, round((OR/ORLow),5)]
        # The change in the current day from start to end (not just one bar, but whole day)
        lastBarClose = currDay.iloc[-1].close
        dayChange = round(((lastBarClose - firstBarOpen) / firstBarOpen), 5)
        # Remaining data
        dayLow = min(currDay[openingRange:].low)
        dayHigh = max(currDay[openingRange:].high)
        #Assign
        columns.append('% OR L->Day Low')
        data.append(round((ORLow - dayLow)/dayLow,5))
        columns.append('% OR H->Day High')
        data.append(round((ORHigh - dayHigh)/dayHigh,5))
        columns.append('Day Low')
        data.append(dayLow)
        columns.append('Day High')
        data.append(dayHigh)
        columns.append('C')
        data.append(currDay.iloc[-1].close)
        columns.append('Volume')
        data.append(sum(currDay.volume))
        # Append to list
        dictList.append(dict(zip(columns, data)))
    # Covnert to dataframe
    pd.DataFrame.from_dict(dictList).to_csv(destination + symbol.replace('.csv', '_OR_' + str(openingRange) + 'bars.csv'), index=False)
