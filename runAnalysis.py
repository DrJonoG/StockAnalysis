
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

''' Weekly update file '''
''' Process historic data '''
''' Analysis for stock data for previous week '''

import os
import sys
import glob
import inspect
import pandas as pd
# Import custom
import analysis.Stats as stats
import analysis.OpeningRange as OR
import analysis.Patterns as patterns
from helpers import LoadIndicators, SymbolIteratorFiles

def Analyse(dataPath, timeFrames):
    for tf in timeFrames:
        source = dataPath + "/" + tf[:2] + "/"
        destination = source + "/analysis/"
        # Create folder if not exists
        if not os.path.exists(destination):
            os.makedirs(destination)
        # Obtain all file names without path
        fileList = [os.path.basename(x) for x in glob.glob(source + "*.csv")]
        # Iterate all files and analyse Arguments [source, destination, marketOnly]
        SymbolIteratorFiles(fileList, patterns.Analyse, [source, destination, True], prefix='Analysing Stats ')
        SymbolIteratorFiles(fileList, stats.Analyse, [source, destination, True], prefix='Analysing Stats ')
        #SymbolIteratorFiles(fileList, OR.Analyse, [source, destination, 15, True], prefix='Analysing Stats ')

if __name__ == '__main__':
    # Clear screen prior to execution
    clear = lambda: os.system('cls')
    clear()

    # Source of all data
    dataPath = 'D:/00.Stocks/data/alpha/'
    # Timeframes
    timeFrames = ['1min']
    # Symbol list
    symbolFileList = ['./config/symbols.csv']

    Analyse(dataPath, timeFrames)
