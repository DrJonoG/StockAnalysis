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

import SymbolData as SD
import ComputeIndicators as CI
import os

if __name__ == '__main__':
    # Download varialbles
    destinationPath = "./downloads/"
    masterDestination = "./master/"
    tickerList = ["./files/NASDAQ.csv", "./files/NYSE.csv"]

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


    # Clear screen prior to execution
    clear = lambda: os.system('cls')
    clear()

    # Download data
    symbolData = SD.SymbolData(destinationPath)
    symbolDF = symbolData.DownloadSymbolData(dataRange='60d', dataInterval='5m', symbolList=["AMC", "AAPL","ALF"], source="yahoo", destinationPath=None)
    #symbolData.MergeDataFiles(masterDestination)

    # Indicators
    tickerIndicators = CI.ComputeIndicators(**indicators)
    tickerIndicators.Compute(symbolDF, "./downloads/files/")
