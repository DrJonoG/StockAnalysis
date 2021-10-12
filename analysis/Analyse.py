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

# analysis of the impact of the previous day close, to the current day based on the opening bar

import os
import time
import datetime
import pandas as pd
from pathlib import Path
from helpers import csvToPandas, PrintProgressBar
from analysis import Gappers

class Analyse:
    def __init__(self):
        pass

    def Run(self, function, input, destinationPath=None):
        """
	    Generic analysis function to support both dictionary of dataframes or a file path

        Parameters
        ----------
        function : Object
            An object from analysis to use to calculate desired function
        input : Dictionary or String
            Either a dictionary of dataframes or a file path to csvs
        destinationPath: String
            The destination to save the CSV files
        """
        # variables
        marketOnly = True
        # Call
        if isinstance(input, dict):
            self.DictionaryIterator(function, input)
        else:
            self.FileIterator(function, input, destinationPath)


    def DictionaryIterator(self, function, input):
        """
	    Iterates through the dictionary and performs analysis

        Parameters
        ----------
        function : Object
            An object from analysis to use to calculate desired function
        input : Dictionary or String
            A dictionary of dataframes of symbol data with indicators
        """
        # Timer
        start = time.time()
        dictList = list()
        inputCount = len(input)
        for index, symbol in enumerate(input):
            PrintProgressBar(index, inputCount, prefix = '==> Analysing: ' + str(symbol).ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            # Get dataframe
            symbolDF = input[symbol]
            # Analyse dataframe
            data, columns = function.Analyse(symbolDF)
            dictList.append(dict(zip(columns, data)))
        PrintProgressBar(inputCount, inputCount, prefix = '==> Analysis complete    ', suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
        # Covnert to dataframe
        return pd.DataFrame.from_dict(dictList)


    def FileIterator(self, function, input, destinationPath):
        """
	    Iterates through the files in the input path and performs analysis on desired function

        Parameters
        ----------
        function : Object
            An object from analysis to use to calculate desired function
        input : String
            File path to csv files with calculated indicators
        destinationPath: String
            The destination to save the CSV files
        """
        if not destinationPath:
            print("==> Error: Destination must be specififed for this operation.")
            exit()
        # Timer
        start = time.time()
        # Check if destination exists
        if destinationPath and not os.path.exists(destinationPath):
            os.makedirs(destinationPath)
        # Get file list
        files = list(Path(input).rglob('*.csv'))
        fileCount = len(files)
        # Iterate through each of the csv files
        for index, filePath in enumerate(files):
            fileName = Path(filePath).name
            PrintProgressBar(index, fileCount, prefix = '==> Analysing: ' + str(fileName).ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            symbolDF = csvToPandas(filePath)
            data, columns = function.Analyse(symbolDF)
            data.to_csv(destinationPath + fileName, index=False)
        PrintProgressBar(fileCount, fileCount, prefix = '==> Analysis complete    ', suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
