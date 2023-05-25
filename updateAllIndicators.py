
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
import multiprocessing
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
    timeFramesAlpha = ['1min', '2min', '15min','60min'] # , '5min', '15min', '30min', '60min'

    # Iterate time frames
    for i in range(0, len(timeFramesAlpha)):
        print(f"==> Updating data for {timeFramesAlpha[i]}")
        path = dataPath + timeFramesAlpha[i][:-2]
        # (symbol, destination, dataInterval, month, year)
        indicators = CI.ComputeIndicators(**LoadIndicators())
        CI.ComputeIndicators(**LoadIndicators()).Compute(source=path, frequency=timeFramesAlpha[i], update=False, destination=path)
