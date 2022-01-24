
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
import core.GetData as getData
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
    symbolFileList = [config['filepath']['symbolList']]

    # Whether to download new data
    downloadData = False
    timeFramesAlpha = ['1min', '5min', '15min', '30min', '60min'] # , '5min', '15min', '30min', '60min'
    # Whether to create custom time frames
    customTimes = True
    customTimeFrames = ['2min']
    # Timeframes
    # Whether to compute the indicators for the corresponding timeframe
    computeIndicators = True

    # update
    update = Update.UpdateData(**LoadIndicators())
    # Update data and download most recent
    # Updates the indicators as specified in settings (./config/indicators.ini)
    if downloadData:
        for i in range(0, len(timeFramesAlpha)):
            print(f"==> Updating data for {timeFramesAlpha[i]}")
            # (symbol, destination, dataInterval, month, year)
            SymbolIterator(symbolFileList, update.Update, [dataPath + timeFramesAlpha[i][:-2], timeFramesAlpha[i], 1, 1], apiCap=150, functionCalls=1)

    # Update custom time frames
    if customTimes:
        data = getData.GetData('./config/api.conf')
        # Create other timeframes
        for custom in customTimeFrames:
            # Destination path and creation of folder
            destination = dataPath + custom[:2] + '/'
            if not os.path.isdir(destination):
                os.mkdir(destination)
            # Iterate through files and create corresponding custom time frame csvs
            # arguments [timeframe, destination path, source path]
            if computeIndicators:
                indicators = CI.ComputeIndicators(**LoadIndicators())
                CI.ComputeIndicators(**LoadIndicators()).Compute(source=destination, frequency=custom, update=False, destination=destination)
                #SymbolIterator(symbolFileList, indicators.Compute, [custom], prefix='Grouping Times', apiCap=150, functionCalls=0)
            exit()
            SymbolIterator(symbolFileList, data.CalculateMinutes, [custom, destination, dataPath + '1m/'], prefix='Grouping Times')
