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

# analysis of the impact of the previous day close, to the current day based on the opening bar

import os
import time
import datetime
import pandas as pd
from pathlib import Path
from helpers import csvToPandas, PrintProgressBar

class Gappers:
    def __init__(self):
        """
        => Opening Price Signal looks at how the gap between open and close impacts the remainder of the day.
        => Does a large gap up result in a closure of the gap in the day?
        => If so, typically when is this gap closed and what happens next
        """
        pass

    def Analyse(self, df, barComparison=24, marketOnly=True):
        """
	    A function to calculate opening range, gaps, and the changes throughout the day

        Parameters
        ----------
        df : Dataframe
            A dataframe for a single symbol
        barComparison : Int
            The number of bars to analyse at intraday i.e. if 5 is selected the first 5 bars are displayed
        marketOnly : Bool
            A boolean to use only market opening hours (if true) or all times (if false)
        """
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
            # Get the days
            currDay = groupedDF[index][1]
            yDay = groupedDF[index-1][1]
            # If only looking at open data, filter out the rest
            if marketOnly:
                currDay = currDay[currDay.Market == 1]
                yDay = yDay[yDay.Market == 1]
            # The change in the previous day between open and close
            yClose = yDay.iloc[-1].close
            yOpen = yDay.iloc[0].open
            yChange = round(((yClose - yOpen) / yOpen)*100, 2)
            # The gap between yesterday day close and market open
            firstBarOpen = currDay.iloc[0].open
            gap = round(((firstBarOpen - yClose) / yClose)*100, 2)
            # Assignment
            data = [currDay.index[0].strftime('%Y-%m-%d'), yOpen, yClose, yChange, (yClose - yOpen), yDay.iloc[-1].RSI14,firstBarOpen, gap, (firstBarOpen - yClose)]
            # The change in the current day from start to end (not just one bar, but whole day)
            lastBarClose = currDay.iloc[-1].close
            dayChange = round(((lastBarClose - firstBarOpen) / firstBarOpen)*100, 2)
            # Assignment
            columns.append('Gap Filled')
            # Check if gap has been filled and what time
            gapFill = currDay[currDay.low <= yClose].head(1)
            if gapFill.empty:
                data.append("Not filled")
            else:
                data.append(gapFill.index[0].strftime('%H:%M'))
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
        # Covnert to dataframe
        return pd.DataFrame.from_dict(dictList), columns
