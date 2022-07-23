
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
import configparser
import pandas as pd
# Import custom
import analysis.OutputCharts as output
from helpers import LoadIndicators, SymbolIteratorFiles

def Analyse(dataPath, timeFrames):
    for tf in timeFrames:
        source = dataPath + "/" + tf[:-2] + "/"
        destination = source + "/analysis/"
        # Create folder if not exists
        if not os.path.exists(destination):
            os.makedirs(destination)

        # Obtain all file names without path
        fileList = [os.path.basename(x) for x in glob.glob(source + "*.csv")]

        # create output folder
        outputFolder = destination + '/output/'
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder + 'figures/')

        # Iterate symbols
        SymbolIteratorFiles(fileList, output.Analyse, [source, outputFolder, True], prefix='Saving ' + tf[:-2] + ' charts ' )


if __name__ == '__main__':
    # Clear screen prior to execution
    clear = lambda: os.system('cls')
    clear()

    # Config
    config = configparser.ConfigParser()
    config.read('./config/source.ini')

    # Source of all data
    dataPath = config['filepath']['indicatorDestination']

    # Timeframes
    timeFrames = ['5min']

    # Symbol list
    symbolFileList = config['filepath']['symbolList']

    Analyse(dataPath, timeFrames)
