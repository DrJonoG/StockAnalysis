
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
from helpers import csvToPandas

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
    # Load DF
    df = csvToPandas(source + symbol)
    # Specify output columns
    columns = ['Datetime', 'yOpen', 'yClose', 'yChange (%)', 'yChange($)', 'yClose RSI', 'Day Open', 'Gap (%)', 'Gap ($)']
    # Empty dictionary list for storage
    dictList = list()
    # Group on date intraday analysis
    groupedDF = df.groupby(df.index.date, group_keys=False)
    # Number of days
    totalDays = groupedDF.ngroups
    # Daily statistics
    dailyStats = groupedDF.close.agg(['max', 'min', 'count', 'median', 'mean'])
    # Convert to list
    groupedDF = list(groupedDF)
    # Iterate through groups, skip first two groups for lookback
    for index in range(2, len(groupedDF)):
        try:
            # Get the days
            currDay = groupedDF[index][1]
            yDay = groupedDF[index-1][1]
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
            # Calculate change
            yChange = round(((yClose - yOpen) / yOpen), 5)
            # The gap between yesterday day close and market open
            firstBarOpen = currDay.iloc[0].open
            gap = round(((firstBarOpen - yClose) / yClose), 5)
            # Assignment
            data = [currDay.index[0].strftime('%Y-%m-%d'), yOpen, yClose, yChange, (yClose - yOpen), yDay.iloc[-1].RSI14,firstBarOpen, gap, (firstBarOpen - yClose)]
            # The change in the current day from start to end (not just one bar, but whole day)
            lastBarClose = currDay.iloc[-1].close
            dayChange = round(((lastBarClose - firstBarOpen) / firstBarOpen), 5)
            # Assignment
            columns.append('Gap Filled')
            # Check if gap has been filled and what time
            gapFill = currDay[currDay.low < yClose].head(1)
            if gapFill.empty:
                data.append("Not filled")
            else:
                data.append(gapFill.index[0].strftime('%H:%M'))
            # Check if gap has been reached and what time:
            columns.append('Gap Reached')
            currDayRemainder = currDay[1:] # We exclude the first bar (the gap) as in theory this will always be touched
            gapTouched = currDayRemainder[currDayRemainder.low < firstBarOpen].head(1)
            if gapTouched.empty:
                data.append("Not touched")
            else:
                data.append(gapTouched.index[0].strftime('%H:%M'))
            # High and lows of the day
            columns.append('Day High')
            data.append(max(currDay.high))
            columns.append('Day Low')
            data.append(min(currDay.low))
            # The clsoe and entire day change
            columns.append('Day Close')
            data.append(lastBarClose)
            columns.append('Day Change')
            data.append(dayChange)
            columns.append('Volume')
            data.append(sum(currDay.volume))
            # Append to list
            dictList.append(dict(zip(columns, data)))
        except Exception:
            print(f"\n ==> Error processing {symbol}\n")
            continue
    # Covnert to dataframe and save appending 'GAP' to file name
    pd.DataFrame.from_dict(dictList).to_csv(destination + symbol.replace('.csv', '_GAP.csv'), index=False)
