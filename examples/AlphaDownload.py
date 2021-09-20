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

# Simple example to download symbol data from AlphaVantage obtaining all historic data
import os
import sys
import time
import datetime
import inspect
import pandas as pd
# Setup
currentDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentDir = os.path.dirname(currentDir)
sys.path.insert(0, parentDir)
# Import custom
import DownloadData as DL
import ComputeIndicators as CI
import data.Alpha as A
from helpers import LoadTickerNames, PrintProgressBar

if __name__ == '__main__':
    start = time.time()
    # Download varialbles
    destinationPath = "../downloads/"
    tickerList = ["../data/SymbolList.csv"]
    alpha = A.Alpha('../docs/api.conf')

    # If saving, make folders
    if destinationPath:
        if not os.path.exists(destinationPath):
            os.makedirs(destinationPath)

    # Load in the ticker list
    symbolList = pd.Series(dtype="float64")

    # Iterate list and load csv if file list, or append string otherwise
    for t in tickerList:
        symbolList = symbolList.append(LoadTickerNames(t, 0), ignore_index=True)
    symbolList = symbolList.drop_duplicates()
    symbolCount = len(symbolList)

    # Dictionary to return data if not saving
    symbolData = {}
    # Iterate through symbolList and download data
    print("==> Please be patient, this may take some time.")
    for index, symbol in symbolList.items():
        PrintProgressBar(index, symbolCount, prefix = '==> Downloding: ' + symbol.ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
        alpha.DownloadExtended(symbol, destinationPath, 5, month='*', year='1', merge=True)
    # End
    PrintProgressBar(symbolCount, symbolCount, prefix = '==> Downloading complete ', suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
