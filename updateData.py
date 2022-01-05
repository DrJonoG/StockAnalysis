
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

''' Daily update file '''

import os
import sys
import inspect
import pandas as pd
import configparser
# Import custom
import core.GetIndicators as CI
import core.GetData as D
import core.GetUpdate as Update
from helpers import LoadIndicators, SymbolIteratorFiles, SymbolIterator


if __name__ == '__main__':
    # Clear screen prior to execution
    clear = lambda: os.system('cls')
    clear()

    # Config
    config = configparser.ConfigParser()
    config.read('./config/source.ini')

    # Source of all data
    dataPath = config['filepath']['dataSource']

    # Config
    symbolFileList = config['filepath']['symbolList']
    data = D.GetData('./config/api.conf')

    # Whether to download new data
    downloadData = True
    timeFramesAlpha = ['1min','5min', '15min', '30min', '60min'] # , '5min', '15min', '30min', '60min'
    # Whether to create custom time frames
    customTimes = True
    customTimeFrames = ['2min']
    # Timeframes
    # Whether to compute the indicators for the corresponding timeframe
    computeIndicators = True


    # update
    update = Update(**LoadIndicators())

    exit()

    # Update data and download most recent
    if downloadData:
        for i in range(0, len(timeFramesAlpha)):
            print(f"==> Updating data for {timeFramesAlpha[i]}")
            # arguments [destination, timeframe, month, year, merge, skipExsiting]
            SymbolIterator(symbolFileList, data.DownloadExtended, [dataPath + timeFramesAlpha[i][:-2], timeFramesAlpha[i], 1, 1, True, False], apiCap=150, functionCalls=1)

    # Update custom time frames
    if customTimes:
        # Create other timeframes
        for custom in customTimeFrames:
            # Destination path and creation of folder
            destination = dataPath + custom[:2] + '/'
            if not os.path.isdir(destination):
                os.mkdir(destination)
            # Iterate through files and create corresponding custom time frame csvs
            # arguments [timeframe, destination path, source path]
            SymbolIterator(symbolFileList, data.CalculateMinutes, [custom, destination, dataPath + '1m/'], prefix='Grouping Times')

    if computeIndicators:
        # Create timeframe data and compute indicators
        for i in range(0, len(timeFramesAlpha)):
            # Merge values to generate timeframes
            path = f'D:/00.Stocks/data/alpha/{timeFramesAlpha[i][0:-2]}_ind/'
            # This function call also fills in all missing data i.e. where volume is 0
            CI.ComputeIndicators(**LoadIndicators()).Compute(source=dataPath, frequency=timeFramesAlpha[i], update=False, destination=path )
