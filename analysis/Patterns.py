
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

# TODO: improve efficiency

import os
import time
import numpy as np
import pandas as pd
from helpers import csvToPandas
from datetime import datetime, timedelta


def Analyse(symbol, source, destination, marketOnly=True, pattern=[1, 1, -1, 1]):
    """
    A function to calculate opening range, gaps, and the changes throughout the day

    Parameters
    ----------
    symbol : String
        The path to the csv file to analyse
    destinationPath : String
        Path to where to save the analysis
    marketOnly : Bool
        A boolean to use only market opening hours (if true) or all times (if false)
    """
    # Ensure pattern is at least 2
    patternLength = len(pattern)
    if patternLength < 2:
        return
    # Load DF
    df = csvToPandas(source + symbol)
    # Open market only
    df = df[df.Market == 1]
    df['Pattern'] = 0
    # Iterate days
    start= time.time()
    count = 0
    # Total risk per trade
    totalRisk = 200
    perShareAdjustment = 0.05
    # Stats
    PnL = 0
    Trades = 0
    Stops = 0
    Profits = 0
    ''' The profit target is risk per share * profit target, i.e. risk 200
    get 400 with a ProfitTarget of 2'''
    ProfitTarget = 2
    # Accumulative
    accumCalculation = True
    if accumCalculation:
        PnL = 10000
    riskPercent = 0.03
    # List PnL change
    ProfitLossList = np.array([])
    # Iterate through each day
    for idx, day in df.groupby(df.index.date):
        # Convert columns to numpy
        Date = day.index.to_numpy()
        CandleDir = day.Candle.to_numpy()
        Close = day.close.to_numpy()
        Low = day.low.to_numpy()
        Volume = day.volume.to_numpy()
        # Find pattern within the day
        pullbackIdx = [i for i in range(0,len(CandleDir)) if list(CandleDir[i:i+patternLength])==pattern]
        # If pattern found len > 0
        if len(pullbackIdx) > 0:
            # For every pullback found
            for y in range(0, len(pullbackIdx)):
                # Index of pullback within the day
                pbStartIdx = pullbackIdx[y]
                # Check if this is already a trade
                if df.at[Date[pbStartIdx], 'Pattern'] != 0:
                    break
                # Get the red candle and entry candle indexes
                redCandleIdx = pbStartIdx+pattern.index(-1)
                entryCandleIdx = pbStartIdx+patternLength-1
                # Check the red candle has less volume that the entry candle
                if Volume[redCandleIdx] < Volume[entryCandleIdx]:
                    # Calculate risk for stop loss
                    riskPerShare = round((Close[entryCandleIdx] - Low[redCandleIdx]) + perShareAdjustment, 2)

                    # Occasionally risk per share may be 0, skip this.
                    if riskPerShare == 0: break

                    # Whether we wish to use accumulative pnl
                    # Determine number of shares to buy
                    if accumCalculation:
                        shareSize = round((PnL * riskPercent) / riskPerShare, 2)
                    else:
                        shareSize = round(totalRisk / riskPerShare, 2)

                    # Define target price
                    targetPrice = Close[entryCandleIdx] + (riskPerShare * ProfitTarget)
                    # Define stop price
                    stopPrice = Low[redCandleIdx] - riskPerShare
                    # Update total trades
                    Trades = Trades + 1

                    # Update dataframe with new column
                    for j in range(pbStartIdx, redCandleIdx):
                        df.at[Date[j], 'Pattern'] = 'Pattern'
                    df.at[Date[pbStartIdx], 'Pattern'] = 'Start'
                    df.at[Date[redCandleIdx], 'Pattern'] = 'Pullback'
                    df.at[Date[entryCandleIdx], 'Pattern'] = 'Entry'

                    # Iterate through minutes whilst in trade
                    for minIdx in range(entryCandleIdx,len(Close)):
                        if Low[minIdx] < stopPrice:
                            df.at[Date[minIdx], 'Pattern'] = 'Stopped'
                            if accumCalculation:
                                PnL = PnL - (PnL * riskPercent)
                            else:
                                PnL = PnL - totalRisk
                            ProfitLossList = np.append(ProfitLossList,PnL)
                            Stops = Stops + 1
                            break
                        elif Close[minIdx] >= targetPrice or minIdx == len(Close)-2:
                            df.at[Date[minIdx], 'Pattern'] = 'Sold'
                            PnL = PnL + ((Close[minIdx] * shareSize) - (Close[entryCandleIdx] * shareSize))
                            ProfitLossList = np.append(ProfitLossList,PnL)
                            Profits = Profits + 1
                            break
                        else:
                            df.at[Date[minIdx], 'Pattern'] = shareSize

    f = open(destination + 'Summary.csv.', "a")
    f.write("%s, %.2f, %.0f, %.0f, %.0f" %(symbol, PnL, Trades, Profits, Stops))
    f.close()
    np.savetxt(destination + symbol.replace(".csv", "_PNL.csv"), ProfitLossList, delimiter=",", fmt='%s')
