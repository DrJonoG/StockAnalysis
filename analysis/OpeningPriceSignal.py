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

class OpeningPriceSignal:
    def __init__(self):
        pass

    def Analyse(self, input, destinationPath=None):
        """

        """
        # output Storage
        columns = ['Datetime', 'Y Open', 'Y Close', 'Y Change (%)', 'Y Close RSI', 'Gap C->O', 'Bar 0 Open', 'Bar 0 Close', 'Bar 0 Change %',
            'Day Close', 'Day Change', 'Bar 1 Open', 'Bar 1 Close', 'Bar 1 Change %', 'Bar 2 Open', 'Bar 2 Close', 'Bar 2 Change %', 'Bar 3 Open', 'Bar 3 Close', 'Bar 3 Change %']
        outputDF = pd.DataFrame(columns=columns)
        # variables
        marketOnly = True
        # Timer
        start = time.time()
        # Iterate through each of the dataframes
        if isinstance(input, dict):
            dictList = list()
            inputCount = len(input)
            for index, symbol in enumerate(input):
                PrintProgressBar(index, inputCount, prefix = '==> Analysing :' + str(symbol).ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
                # Get dataframe
                symbolDF = input[symbol]
                # Analyse dataframe
                data = self.AnalyseDF(symbolDF, columns)
                dictList.append(dict(zip(columns, data)))
            PrintProgressBar(inputCount, inputCount, prefix = '==> Analysis complete    ', suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            # Covnert to dataframe
            return pd.DataFrame.from_dict(dictList)
        else:
            # Check if destination exists
            destinationPath += 'OpeningPriceSignal/'
            if destinationPath and not os.path.exists(destinationPath):
                os.makedirs(destinationPath)
            # Get file list
            files = list(Path(input).rglob('*.csv'))
            fileCount = len(files)
            # Iterate through each of the csv files
            for index, filePath in enumerate(files):
                fileName = Path(filePath).name
                PrintProgressBar(index, fileCount, prefix = '==> Analysing :' + str(fileName).ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
                symbolDF = csvToPandas(filePath)
                data = self.AnalyseDF(symbolDF, columns)
                data.to_csv(destinationPath + fileName)
            PrintProgressBar(fileCount, fileCount, prefix = '==> Analysis complete    ', suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))

    def AnalyseDF(self, df, columns, marketOnly=True):
        """

        """
        # Empty dictionary list for storage
        dictList = list()
        # Group on date
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
            prevDay = groupedDF[index-1][1]
            prevPrevDay = groupedDF[index-2][1]
            # If only looking at open data, filter out the rest
            if marketOnly:
                currDay = currDay[currDay.Market == 1]
                prevDay = prevDay[prevDay.Market == 1]
            # The change in the previous day between open and close
            yClose = prevDay.iloc[-1].close
            yOpen = prevDay.iloc[0].open
            yChange = round(((yClose - yOpen) / yOpen)*100, 2)
            # The gap between prev day close and market open
            firstBarOpen = currDay.iloc[0].open
            gap = round(((firstBarOpen - yClose) / yClose)*100, 2)
            # First bar analysis comparing the close to open
            firstBarClose = currDay.iloc[0].close
            firstBarChange = round(((firstBarClose - firstBarOpen) / firstBarOpen)*100, 2)
            # The change in the current day
            lastBarClose = currDay.iloc[-1].close
            dayChange = round(((lastBarClose - firstBarOpen) / firstBarOpen)*100, 2)
            # Assignment
            data = [currDay.index[0].strftime('%Y-%m-%d'), yOpen, yClose, yChange, prevDay.iloc[-1].RSI14, gap, firstBarOpen, firstBarClose, firstBarChange, lastBarClose, dayChange]
            # Append to list
            dictList.append(dict(zip(columns, data)))
        # Covnert to dataframe
        return pd.DataFrame.from_dict(dictList)
