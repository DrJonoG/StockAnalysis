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


# Simple example to download symbol data and compute indicators for these.
import os
import sys
import inspect
import pandas as pd
# Setup
currentDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentDir = os.path.dirname(currentDir)
sys.path.insert(0, parentDir)
# Import custom
import DownloadData as DL
import ComputeIndicators as CI

if __name__ == '__main__':
    # Download varialbles
    dataSource = 'yahoo'
    destinationPath = "./downloads/"
    tickerList = ["./files/SymbolList.csv"]

    # Create download instance
    symbolData = DL.DownloadData(dataSource)
    # Downloads data and stores in variable, doesn't save as a file
    symbolDF = symbolData.Download(dataRange='60d', dataInterval='5m', symbolList=['AMC'])
    # Alternatively this approach downloads symbol data, appends to existing file it exists.
    # symbolDF = symbolData.Download(dataRange='60d', dataInterval='5m', symbolList=tickerList, destinationPath=destinationPath + '5m/')

    # Inidcator varialbles
    indicatorDestination = "./indicators/"
    indicators = {
        'expMovingAverage': [3, 5, 10, 20, 50, 100],
        'simpleMovingAverage': [5, 10, 20, 50, 100],
        'rsiLength': 14,
        'bollingerPeriod': 20,
        'bollingerStdDev': 1.5,
        'vWAP': True,
        'precision': 2
    }

    # Indicator Initialise
    symbolIndicators = CI.ComputeIndicators(**indicators)
    # Compute indicators on variable
    indicatorDF = symbolIndicators.Compute(symbolDF)
    # Display
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.max_columns', None)
    print(indicatorDF)
