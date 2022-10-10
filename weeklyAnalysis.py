
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
import analysis.Stats as stats
import analysis.OpeningRange as OR
import analysis.Patterns as patterns
import analysis.MAPullback as pullback
import analysis.Gappers as gappers
import analysis.OutputCharts as output
import analysis.HOD as hod
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

        HODFolder = destination + '/HOD/'
        if not os.path.exists(HODFolder):
            os.makedirs(HODFolder + 'figures/')

        #hod.Analyse(symbol, source, destination, hodBars, ORBars, marketOnly=True, outputFigures=False):
        hodBars = 1
        ORBars = 5

        SymbolIteratorFiles(fileList, hod.Analyse, [source, HODFolder, hodBars, ORBars, True, True], prefix='Analysing ' + tf[:-2] + ' HOD ' )
        hod.AnaylseResults(destination + '/HOD/', f'{hodBars}PB_{ORBars}OR_Raw.csv')


        exit()

        ORBFolder = destination + '/ORB/'
        if not os.path.exists(ORBFolder):
            os.makedirs(ORBFolder + 'figures/')
        SymbolIteratorFiles(fileList, orb.Analyse, [source, ORBFolder, True], prefix='Analysing ' + tf[:-2] + ' ORB ' )



        # Iterate all files and analyse Arguments [source, destination, marketOnly]
        #SymbolIteratorFiles(fileList, gappers.Analyse, [source, destination + 'gappers/', True], prefix='Analysing Gappers ')
        # Summarise gapper results
        #summary.Gappers(destination)


        # Arguments: [source, destination, openingRange=3, marketOnly=True]

        #hod.AnaylseResults(destination + '/HOD/', 'HOD_Analysis.csv','Analysis_2PB_5OR.csv')
        #exit()

        # Iterate all files and analyse Arguments [source, destination, numberOfBars, marketOnly]
        #SymbolIteratorFiles(fileList, OR.Analyse, [source, destination +  'openingrange/', 5, True], prefix='Analysing Opening Range ')
        # Summarise opening range
        #summary.OpeningRange(destination)

        # Iterate all files and analyse Arguments [source, destination, marketOnly]
        #patternFolder = destination + '/patterns/'
        #if not os.path.exists(patternFolder):
        #    os.makedirs(patternFolder + 'figures/')
        #SymbolIteratorFiles(fileList, patterns.Analyse, [source, patternFolder, True], prefix='Analysing ' + tf[:-2] + ' Patterns ' )
        #MAPBFolder = destination + '/pullback/'
        #if not os.path.exists(MAPBFolder):
        #    os.makedirs(MAPBFolder + 'figures/')
        #SymbolIteratorFiles(fileList, pullback.Analyse, [source, MAPBFolder, True], prefix='Analysing ' + tf[:-2] + ' MA Pullback ' )


        #ORBFolder = destination + '/ORB/'
        #if not os.path.exists(ORBFolder):
        #    os.makedirs(ORBFolder + 'figures/')
        #SymbolIteratorFiles(fileList, orb.Analyse, [source, ORBFolder, True], prefix='Analysing ' + tf[:-2] + ' ORB ' )
        #SymbolIteratorFiles(fileList, pullback.Analyse, [source, MAPBFolder, True], prefix='Analysing ' + tf[:-2] + ' MA Pullback ' )
        #pullback.Summary(MAPBFolder, destination)
        #patterns.Summary(patternFolder, destination)
        #exit()
        # Don't need stats.Analyse until trading regularly, provides more of an overview of last month
        #SymbolIteratorFiles(fileList, stats.Analyse, [source, destination, True], prefix='Analysing Stats ')


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
    timeFrames = ['2min']

    # Symbol list
    symbolFileList = config['filepath']['symbolList']

    Analyse(dataPath, timeFrames)
