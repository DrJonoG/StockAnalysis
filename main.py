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
import core.DownloadData as DL
import core.ComputeIndicators as CI
from analysis import Analyse, Pullback, Gappers, AnalysisSummary
from helpers import LoadIndicators, SymbolIteratorFiles

if __name__ == '__main__':
    fromSource = False
    fromFiles = True
    # Clear screen prior to execution
    clear = lambda: os.system('cls')
    clear()

    '''
    Example 1: From source
    '''
    if fromSource:
        print("====> Example 1: From Source")
        # initialise download class and specified alpha as source
        # Download data for a single symbol
        df = DL.DownloadData('alpha').Download(60, '5m', ['AMC', 'ALF'])
        # Compute indicators on variable
        df = CI.ComputeIndicators(**LoadIndicators()).Compute(df)
        # Opening Price signal Analysis
        opsDF = Analyse.Analyse().Run(Gappers.Gappers(), df)

    '''
    Example 2: From CSV, saves harddrive
    '''
    print("====> Example 2: From Files")
    if fromFiles:
        # input and output directories
        input = r'D:\00.Stocks\testing\data'
        out_indicators = r'D:\00.Stocks\testing\indicators\\'
        out_analysis = r'D:\00.Stocks\testing\analysis\Gappers\\'
        # Compute the indictators and save to indicators directory
        #CI.ComputeIndicators(**LoadIndicators()).Compute(input, out_indicators)
        # Compute the opening price signal and save to analysis
        Analyse.Analyse().Run(Gappers.Gappers(), out_indicators, out_analysis)
        #Analyse.Analyse().Run(Pullback.Pullback(), out_indicators, out_analysis)
        # Summarise
        summary = AnalysisSummary.AnalysisSummary()
        summary.Gappers(out_analysis)
