
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

''' Historic update file '''
''' Download all data for all symbols '''

import os
import sys
import inspect
import configparser
import pandas as pd
# Import custom
import core.GetIndicators as CI
import core.GetData as data
from helpers import LoadIndicators, SymbolIterator


def Historic(dataPath, symbolFileList, alpha, timeFramesAlpha):
    # Download all data for all sybols
    for i in range(0, len(timeFramesAlpha)):
        print(f"==> Downloading for {timeFramesAlpha[i]}")
        # arguments [destination, timeframe, month, year, merge, skipExsiting]
        SymbolIterator(symbolFileList, alpha.DownloadExtended, [dataPath + timeFramesAlpha[i][:2], timeFramesAlpha[i], '*', '*'], apiCap=150, functionCalls=24)

    # Create timeframe data and compute indicators
    for i in range(1, len(timeFramesAlpha)):
        # Merge values to generate timeframes
        path = dataPath + timeFramesAlpha[i][0:-2] + '/'
        # Compute the indictators and save to indicators directory if true
        if ComputeIndicators[i]:
            # This function call also fills in all missing data i.e. where volume is 0
            CI.ComputeIndicators(**LoadIndicators()).Compute(source=dataPath, frequency=timeFramesAlpha[i], update=False, destination=dataPath)

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

    alpha = data.GetData('./config/api.conf')

    # Whether to download new data
    timeFramesAlpha = ['1min']

    Historic(dataPath, symbolFileList, alpha, timeFramesAlpha)
