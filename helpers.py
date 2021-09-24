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
import numpy as np
import pandas as pd
import datetime
import time

def PrintProgressBar (iteration, total, prefix = '', suffix = '', length = 20):
    """
    Displays a progress bar

    Parameters
    ----------
    iteration : Int
        The current interation
    total : Int
        Total number to iterate
    prefix : String
        The prefix to display
    suffix : String
        The suffix to display
    length : Int
        The length of the progress bar
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = '█' * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = "\r")
    # Add new line at the end
    if total == iteration:
        print("\r")

def ConfigParser(items):
    """
    Formats the configuration file into the correct types

    Parameters
    ----------
    items : List
        A list of the configuration settings
    """
    print(type(items))
    result = []
    for (key, value) in items:
        typeTag = key[:2]
        if typeTag == "s_":
            result.append((key[2:], value))
        elif typeTag == "a_":
            result.append((key[2:], np.fromstring(value, dtype=float, sep=',')))
        elif typeTag == "f_":
            result.append((key[2:], float(value)))
        elif typeTag == "i_":
            result.append((key[2:], int(value)))
        elif typeTag == "t_":
            result.append((key[2:], pd.to_datetime(value).time()))
        elif typeTag == "b_":
            result.append((key[2:], bool(value)))
        else:
            raise ValueError('Invalid type tag "%s" found in ini file.' % typeTag)
    return result


def MergeDataFolders(self, sourcePath, destinationPath):
    """
    Merges files of the same time frame and symbol together.
    Used when data is regularly downloaded as lookback of Yahoo is only 60 days on 5minute interval
    sourcePath should contain a series of directories of different dates

    Parameters
    ----------
    sourcePath : String
        A directory containing the directories of symbols to merge
    destinationPath : String
        The location in which to store the merged files
    """
    folderList = [ f.path for f in os.scandir(sourcePath) if f.is_dir() ]
    if len(folderList) > 1:
        if not os.path.exists(destinationPath):
            os.makedirs(destinationPath)
        # Use glob module to return all csv files under root directory. Create DF from this.
        fileList = pd.DataFrame([file for file in glob.glob(sourcePath + "/*/*")], columns=["fullpath"])
        # Split the full path into directory and filename and join with original into one DataFrame
        fileList = fileList['fullpath'].str.rsplit("\\", 1, expand=True).rename(columns={0: 'path', 1:'filename'}).join(fileList)
        # List of unique files
        uniqueFiles = fileList['filename'].unique()
        countUnique = len(uniqueFiles)
        # Iterate over unique filenames; read CSVs, concat DFs, save file
        start = time.time()
        for i, f in enumerate(uniqueFiles):
            PrintProgressBar(i+1, countUnique, prefix = 'Merging: '  + f.ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            pathList = fileList[fileList['filename'] == f]['fullpath'] # Get list of fullpaths from unique filenames
            dfs = [pd.read_csv(path) for path in pathList] # Get list of dataframes from CSV file paths
            dfConcat = pd.concat(dfs) # Concat dataframes into one
            dfConcat = dfConcat.drop_duplicates(subset=['Datetime'], keep='first').reset_index(drop=True) # Remove duplicate entries
            dfConcat = dfConcat.set_index(pd.DatetimeIndex(dfConcat['Datetime'])).sort_index()
            dfConcat.to_csv(destinationPath + f, index=False) # Save dataframe


def LoadTickerNames(filepath, column=0):
    """
    Loads in a list of tickets from a csv file.

    Parameters
    ----------
    filepath : String
        Location of the csv file containing a list of symbol names
    column : Int
        The column in which the symbol is located, 0 by default.
    """
    # Symbol must be first column
    try:
        df = pd.read_csv(filepath)
        return df.iloc[:, column]
    except Exception as e:
        print("==> Error: invalid or missing ticker file %s. Exiting application." % filepath)
        exit(1)


def SymbolIterator(fileList, function, arguments, prefix='Downloading', apiCap=150, functionCalls=1):
    """
    Iterate through the symbols in fileList and call the function using the arguments provided
    The symbol is always the first argument passed to the function
    Handles the maximum number of calls per minute and sleeps if limit has been reached

    Parameters
    ----------
    fileList : String
        Location of the csv file containing a list of symbol names
    function : Object
        The function to be called
    arguments : List
        A list of arguments to be passed to the function
    prefix : String
        (Optional) String for the progress bar reporting
    apiCap : Int
        (Optional) The number of calls that can be made per minute with your Alpha API key
    functionCalls : Int
        (Optional) The number of api calls the function makes for each invoke
    """
    start = time.time()
    # Load in the ticker list
    symbolList = pd.Series(dtype="float64")

    # Iterate list and load csv if file list, or append string otherwise
    for f in fileList:
        symbolList = symbolList.append(LoadTickerNames(f, 0), ignore_index=True)
    symbolList = symbolList.drop_duplicates()
    symbolCount = len(symbolList)

    # Dictionary to return data if not saving
    symbolData = {}
    # Iterate through symbolList and download data
    print("==> Please be patient, this may take some time.")
    apiCalls = 0
    apiTime = time.time()
    for index, symbol in symbolList.items():
        # Determine seconds
        duration = (time.time() - apiTime)
        # Update number of API calls before it happens
        apiCalls += functionCalls
        # If minute cap is reached, then sleep, else continue
        if duration < 60 and apiCalls > apiCap:
            PrintProgressBar(index, symbolCount, prefix = '==> ' + ('API Limit Reached. Paused: ').ljust(20), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
            time.sleep((60-duration)+2)
        elif duration > 60:
            apiTime = time.time()
            apiCalls = functionCalls
        #
        PrintProgressBar(index, symbolCount, prefix = '==> ' + (prefix + ': ').ljust(10) + symbol.ljust(10), suffix = 'Complete. Runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
        calledAPI = function(symbol, *arguments)
        # If the api wasn't called (i.e. data already exists), deduct call count
        if not calledAPI:
            apiCalls -= functionCalls
        # Todo: May need to add sleep function in if making too many calls per minute.
    PrintProgressBar(symbolCount, symbolCount, prefix = '==> ' + (prefix + ' Complete').ljust(20), suffix = 'Complete. Total runtime: ' + str(datetime.timedelta(seconds = (time.time() - start))))
