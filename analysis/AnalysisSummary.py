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
import numpy as np
import pandas as pd
from pathlib import Path
from helpers import csvToPandas, PrintProgressBar

class AnalysisSummary:
    def __init__(self):
        """
        => Opening Price Signal looks at how the gap between open and close impacts the remainder of the day.
        => Does a large gap up result in a closure of the gap in the day?
        => If so, typically when is this gap closed and what happens next
        """
        pass

    def Gappers(self, directory):
        # Timer
        start = time.time()
        # Define columns
        summaryDFColumns = ['Symbol', '# Days', 'Avg. Vol', 'Min Vol.','Max Vol.', 'Avg. Gap (%)', 'Min Gap (%)', 'Max Gap (%)', '% Filled', 'Avg Fill Time', '% C > yC', '% C > O', '% yC = C', '% C < yC']
        summaryDFData = []
        gapperGroupedColumns = [ 'Gap %', 'Symbol', '# Occurances', '% Occurances', 'Avg. Vol', '% Filled Gap', '% C > yC', '% C > O', 'Avg. Fill Time']
        gapperGroupedData = []
        # Get file list
        files = list(Path(directory).rglob('*.csv'))
        fileCount = len(files)
        # Main df
        dictListSummary = list()
        dictListGaps = list()
        # Iterate through each of the csv files
        for index, filePath in enumerate(files):
            fileName = Path(filePath).name
            if '00' in fileName: continue
            PrintProgressBar(index, fileCount, prefix = '==> Analysing: ' + str(fileName).ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            symbolDF = csvToPandas(filePath)
            # Remove 0 volume days
            symbolDF = symbolDF[symbolDF.Volume > 0]
            numRows = len(symbolDF)
            # Create row
            summaryDFData = [
                fileName,
                numRows,
                round(symbolDF.Volume.mean(), 0),
                min(symbolDF.Volume),
                max(symbolDF.Volume),
                round(symbolDF['Gap (%)'].mean(), 2),
                min(symbolDF['Gap (%)']),
                max(symbolDF['Gap (%)']),
                round((len(symbolDF[symbolDF['Gap Filled'] != 'Not filled']) / numRows)*100,2),
                symbolDF['Gap Filled'].value_counts().nlargest(n=4).index.values,
                round((len(symbolDF[symbolDF['Day Close'] > symbolDF['yClose']]) / numRows)*100,2),
                round((len(symbolDF[symbolDF['Day Close'] > symbolDF['Day Open']]) / numRows)*100,2),
                round((len(symbolDF[symbolDF['Day Close'] == symbolDF['yClose']]) / numRows)*100,2),
                round((len(symbolDF[symbolDF['Day Close'] < symbolDF['yClose']]) / numRows)*100,2)
            ]
            # Append to list
            dictListSummary.append(dict(zip(summaryDFColumns, summaryDFData)))
            gaps = [0.1, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 200.00]
            gaps = np.append(np.flip(np.negative(gaps)), gaps)
            for i in range(1, len(gaps)):
                gapDF = symbolDF[(symbolDF['Gap (%)'] >= gaps[i-1]) & (symbolDF['Gap (%)'] < gaps[i])]
                numRowsG = len(gapDF)
                # Counter division by zero
                if numRowsG == 0: numRowsG = 1
                # Allocate values
                gapperGroupedData = [
                    str(gaps[i-1]) + ' to ' + str(gaps[i]),
                    fileName,
                    numRowsG,
                    round((numRowsG / numRows)*100, 2),
                    round(gapDF.Volume.mean(), 0),
                    round((len(gapDF[gapDF['Gap Filled'] != 'Not filled']) / numRowsG)*100,2),
                    round((len(gapDF[gapDF['Day Close'] > gapDF['yClose']]) / numRowsG)*100,2),
                    round((len(gapDF[gapDF['Day Close'] > gapDF['Day Open']]) / numRowsG)*100,2),
                    gapDF['Gap Filled'].value_counts().nlargest(4,keep='all')
                ]
                # Append to list
                dictListGaps.append(dict(zip(gapperGroupedColumns, gapperGroupedData)))

        PrintProgressBar(fileCount, fileCount, prefix = '==> Analysis complete    ', suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
        # Covnert to dataframe
        pd.DataFrame.from_dict(dictListSummary).to_csv(directory + '00.gappers_summary.csv', index=False)
        pd.DataFrame.from_dict(dictListGaps).to_csv(directory + '00.gappers_grouped.csv', index=False)
