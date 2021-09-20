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

import os
import sys
import inspect
import pandas as pd
# Import custom
import DownloadData as DL
import ComputeIndicators as CI

if __name__ == '__main__':
    # Clear screen prior to execution
    clear = lambda: os.system('cls')
    clear()

    # Download varialbles
    bulkDownload = False
    dataSource = 'yahoo'
    destinationPath = "./downloads/"
    tickerList = ["./files/SymbolList.csv"]

    # Create download instance
    symbolData = DL.DownloadData(dataSource)
    """
    symbolData.Download

    Parameters
    ----------
         symbolList
            a list of file paths to CSVs which contain the symbol or a list of symbols as strings
         destinationPath
            if set saves the data obtained from the source in this directory, will create if it does not exist. If not specified data will be returned instead.
    """
    # Download data
    if bulkDownload:
        symbolData.Download(dataRange='60d', dataInterval='5m', symbolList=tickerList, destinationPath=destinationPath + '5m/')
        symbolData.Download(dataRange='7d', dataInterval='1m', symbolList=tickerList, destinationPath=destinationPath + '1m/')
        symbolData.Download(dataRange='60d', dataInterval='2m', symbolList=tickerList, destinationPath=destinationPath + '2m/')
        symbolData.Download(dataRange='60d', dataInterval='15m', symbolList=tickerList, destinationPath=destinationPath + '15m/')
        symbolData.Download(dataRange='365d', dataInterval='1d', symbolList=tickerList, destinationPath=destinationPath + '1d/')

    # Single file download
    symbolDF = symbolData.Download(dataRange='60d', dataInterval='5m', symbolList=["AMC"])
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
    # Save
    indicatorDF['AMC'].to_csv('./downloads/AMCExample.csv', index=False)
    # Display
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.max_columns', None)
    # Output
    print(indicatorDF['AMC'])

    # Backtesting
    #pbMA = PullbackToMA('./docs/backtesting.ini')
    #pbMA.Run(indicatorDF["A"], "A")
    # Visualise
    #visualise = VD.VisualDisplay("Testing", indicatorDF["AMC"])
    #visualise.CandleStick()
    #visualise.Display()
