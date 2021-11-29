
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

import os
import time
import datetime
import pandas as pd
import numpy as np
import statsmodels.api as sm
import core.Figure as figure
from pathlib import Path
from helpers import csvToPandas, PrintProgressBar


class Pullback:
    def __init__(self):
        pass

    def Analyse(self, df):
        ''' Config Variables '''
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
        groupBy = '2B'
        # crtierias
        barsAboveSupport = 5 # Should at above least [barsAboveSupport] bars to consider entry
        maximumBarsBelow = 6 # If pullback falls below support for [maximumBarsBelow] or more, stop looking for pullback.

        trading_start = '10:00'
        trading_end = '15:00'
        ''' End Config Variables '''

        # Empty dictionary list for storage
        dictList = list()
        # Open market only
        df = df[df.Market == 1]
        # Group on date intraday analysis
        groupedDF = df.groupby(pd.Grouper(freq=groupBy), group_keys=False)
        # Convert to list
        groupedDF = list(groupedDF)
        # initialise figure
        fig = figure.Figure()
        # Iterate through groups, skip first two groups for lookback
        for index in range(1, len(groupedDF)):
            # data
            data = groupedDF[index][1]
            Y = data['close'][20:100]
            X = data.index.values.astype(np.int64)[20:100]
            #X = sm.add_constant(X)
            #model = sm.OLS(Y,X)
            #results = model.fit()
            #print(results.summary())
            #print(results.params)
            #print(results.t_test([1, 0]))

            data['bestfit'] = sm.OLS(Y,X).fit().fittedvalues[20:100]
            data.index = data.index.strftime("%m/%d/%Y %H:%M:%S")
            # Append data to figure
            fig.AppendCandles(data)
            # pullback settings
            support = data['20MA'] # This is the dataset that we're looking for the primary to touch
            pullback = data['close']  # This is what will be making the pullback i.e. the close
            trend = data['50MA'] # This is the crtieria in which the price must be above to even consider a trade
            # Search for possible entry
            # This checks to see if the market is in an uptrend
            criteriaResults = (support > trend) & (pullback > support) # can we start looking for entry positions?
            ## Enter trade
            waitingResults = (criteriaResults) & (pullback < support * 1.01) & (pullback >= support) & (data.open > data.close)
            # Initialise variables - booleans
            inTrade = False
            waiting = False
            entering = False
            searching = True
            #Iterate through each group
            for i in range(barsAboveSupport, len(data)):
                if searching:
                    # Has the criteria been met for barsAboveSupport, if so, look for pullback
                    # This technically looks to see if the current market is trending up
                    if all([x == True for x in criteriaResults[i-barsAboveSupport:i]]):
                        waiting = True
                        searching = False
                elif waiting:
                    '''Criteria of trend met, can we find a pullback'''
                    fig.AddVerticalRect(data.index[i-1],data.index[i], 'rgb(33,39,49)')
                    # if pullback goes below the support for more than maximumBarsBelow the crtieria condition is broken
                    if all([x == False for x in criteriaResults[i-maximumBarsBelow:i]]):
                        waiting = False
                        searching = True
                    elif waitingResults[i]:
                        # Pullback found, wait for entry
                        #waiting = False
                        entering = True
                        #fig.AddVerticalRect(data.index[i-1],data.index[i], "green")
                    else:
                        pass
                        # Continue searching for pullback
                        #fig.AddVerticalRect(data.index[i-1],data.index[i])
                elif entering:
                    pass
                    #fig.AddVerticalRect(data.index[i-1],data.index[i], "green")
                    # Pullback is found, look for an entry
                elif inTrade:
                    pass
                    # We are now in a trade, check if we need to exit


                '''if searchCriteria[i] and not inTrade:
                    fig.AddMarker([data.index[i]], [data.iloc[i].close], '5', 'green', size=20)
                    inTrade = True
                elif not searchCriteria[i] and inTrade:
                    inTrade = False
                    fig.AddMarker([data.index[i]], [data.iloc[i].close], '6', 'red', size=20)'''


            # Draw figure
            fig.AddLine(data, '20MA', name='20MA')
            fig.AddLine(data, '50MA', 'blue', '50MA')
            fig.AddLine(data, 'bestfit', 'red' ,'Bestfit')
            fig.TextConfig()
            fig.Show()
            exit()
