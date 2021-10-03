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
import inspect
# Setup
currentDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentDir = os.path.dirname(currentDir)
sys.path.insert(0, parentDir)
# Import custom
import data.Alpha as A
from helpers import SymbolIterator

if __name__ == '__main__':
    # Clear screen prior to execution
    clear = lambda: os.system('cls')
    clear()
    # Download varialbles
    destinationPath = "../downloads/"
    symbolFileList = ["../config/symbols.csv"]
    alpha = A.Alpha('../config/api.conf')

    # If saving, make folders
    if destinationPath:
        if not os.path.exists(destinationPath):
            os.makedirs(destinationPath)

    # Download maximum data for each symbol
    SymbolIterator(symbolFileList, alpha.DownloadExtended, [destinationPath + '5m/', 5, '*', '*', True], apiCap=150, functionCalls=24)
