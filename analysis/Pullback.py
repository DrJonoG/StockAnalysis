
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
import random
import numpy as np
import pandas as pd
from core import Figure
from pathlib import Path
from helpers import csvToPandas, PrintProgressBar
from datetime import datetime, timedelta

def Analyse(symbol, MAPullback, HighMA, source, destination, marketOnly=True, pattern=[1, 1, -1, 1]):
    """
    A series of possible variables to be tested

    Parameters
    ----------
    symbol : String
        The path to the csv file to analyse
    destinationPath : String
        Path to where to save the analysis
    marketOnly : Bool
        A boolean to use only market opening hours (if true) or all times (if false)
    pattern : array
        The pattern to search for within the data i.e. [1, 1, -1, 1] where 1
        refers to a green candle, -1 a red candle and 0 no price change
    """

    ''' The percetange of total balance to risk per trade '''
    riskPercents = [0.02]

    ''' The patterns to look for and enter on '''
    patterns = [[1, 1, -1, 1], [1, 1, 1, -1, 1]]

    ''' The profit target is risk per share * profit target, i.e. risk 200
    get 400 with a ProfitTarget of 2'''
    profitTargets = [2, 3]

    ''' Price must be above following moving averages, 0 represents ignore '''
    ''' If negative, this indicates price must be below the EMA '''
    priceAboveMAs = ['0', '50EMA']

    ''' MA must be above following moving averages, 0-0 represents ignore
    The first MA must be greater than the second i.e. 10ema-20ema: 10ema should
    be higher than 20ema. '''
    maAboveMAs = ['0-0']

    ''' Above or below vwap '''
    vWAP = [True, False]

    ''' RSI max, value must be below this if true
    Uses default value of 80 '''
    RSIs = [False]

    ''' Entry volume greater than PB volume if true. Red candle(s) should Have
    less volume than '''
    entryVolHigher = [True, False]

    ''' Incremental selling i.e. should we sell 1/3 our position 2/3 of the
    way to the target to take half half profits '''
    incremental = [False]

    ''' Stop limit is the limit willing to risk per share '''
    stopLimits = [0.1,0.2,0.3,0.5]

    ''' Whether to reset PNL each time, if true focus on percent won '''
    resetPNL = [True]

    ''' Whether green bar needs to close above PB '''
    closeAbove = [True, False]

    # Average minimum volume
    minVolume = 2000000
    # How much room to give stop loss from low of pullback
    perShareAdjustment = 0.05
    # Trade costs
    costPerTrade = 5
    # Load DF
    if not os.path.exists(source + symbol): return
    df = csvToPandas(source + symbol)

    # Open market only
    if marketOnly:
        df = df[df.Market == 1]

    # Filter out data over a year old
    # Older dates have less signifcance as markets change
    df = df[df.index > '2021-01-01']

    # log file:
    fileName = MAPullback + '_to_' + HighMA + '_' + symbol[0] + '_Summary.csv'
    if not os.path.exists(destination + fileName):
        with open(destination + fileName, "w") as f:
            f.write("Symbol,Days,IncrementalProfitTaking,MinDayVolume,PnL,Total Profit,Total Loss,PnL Per Trade,# Trades,# Trades Per Day,Reset PNL,# Profits,# Losses,# EOD,# Bust,Win %,Risk %,Stop Limit,Pattern,Profit Target,Price Above MA,MA above MA,vWAP,RSI,Entry Vol > PB Vol,Per Share Adjust.,Cost Per Trade,Positive,CloseAbovePullback\n")

    f = open(destination + fileName, 'a')

    # symbol
    sym = symbol.replace(".csv", "")
    # Iterate all possible combinations
    for riskPercent in riskPercents:
        for pattern in patterns:
            for profitTarget in profitTargets:
                for priceAboveMA in priceAboveMAs:
                    for maAboveMA in maAboveMAs:
                        for vwap in vWAP:
                            for RSI in RSIs:
                                for entryVol in entryVolHigher:
                                    for increm in incremental:
                                        for stopLimit in stopLimits:
                                            for reset in resetPNL:
                                                for above in closeAbove:
                                                    returnLine = runAnalysis(df, MAPullback, HighMA, reset, above, destination, sym, riskPercent, pattern, profitTarget, priceAboveMA, maAboveMA, vwap, RSI, entryVol, increm,  stopLimit, perShareAdjustment, costPerTrade, minVolume)
                                                    if returnLine is not None:
                                                        f.write(returnLine)
    f.close()


def runAnalysis(df, MAPullback, HighMA, reset, closeAboveRed, destination, symbol, riskPercent, pattern, profitTarget, priceAboveMA, maAboveMA, vwap, rsi, entryVol, incremental, stopLimit, perShareAdjustment, costPerTrade, minVolume):
    # Whether to write figures
    # Note, this is computational expensive
    drawFigures = False
    # Logger
    tradeLog = []
    # Set pattern to 0
    df['Pattern'] = 0
    # Length
    patternLength = len(pattern)
    # Stats
    PnL = 0
    Trades = 0
    Stops = 0
    EOD = 0
    Bust = 0
    Profits = 0
    ProfitValue = 0
    LossValue = 0
    Days = 0
    # Accumulative
    startingPNL = 10000
    PnL = startingPNL
    # split string
    maAboveMAsplit = maAboveMA.split('-')
    # Iterate through each day
    for idx, day in df.groupby(df.index.date):
        # Calculate pattern
        df.loc[df[MAPullback] > df[HighMA], 'PB'] = 1
        df.loc[df[MAPullback] < df[HighMA], 'PB'] = -1
        df.loc[df[MAPullback] == df[HighMA], 'PB'] = 0

        # Pandas to numpy
        Volume = day.volume.to_numpy()
        # Check if any entries
        if Volume.shape[0] < 1:
            continue

        # check if average volume below min volume
        if sum(Volume) < minVolume:
            continue

        # Convert columns to numpy
        Days = Days + 1
        Date = day.index.to_numpy()
        CandleDir = day.Candle.to_numpy()
        Close = day.close.to_numpy()
        Open = day.open.to_numpy()
        Low = day.low.to_numpy()

        # Find patterns within the day
        pullbackIdx = [i for i in range(0,len(CandleDir)) if list(CandleDir[i:i+patternLength])==pattern]

        # Daily figure
        if drawFigures:
            figure = Figure.Figure()
            figure.CandleStick(day)
            figure.TextConfig(chartTitle=f"{symbol} : {df.index[0]}")

        # If pattern found len > 0
        if len(pullbackIdx) > 0:
            # For every pullback found
            for y in range(0, len(pullbackIdx)):
                # Whether to reset the PNL, this is useful to fully evaluate and not
                # stop evalaution due to going bust.
                if reset:
                    PnL = startingPNL
                # Index of pullback within the day array
                pbStartIdx = pullbackIdx[y]
                # Get the red candle and min and max values if multi bar pullback
                redCandleIdx = [n+pbStartIdx for n,x in enumerate(pattern) if x==-1]
                redCandleVol = max([Volume[x] for n,x in enumerate(redCandleIdx)])
                redCandleLow = min([Low[x] for n,x in enumerate(redCandleIdx)])
                # Entry candle
                entryCandleIdx = pbStartIdx+patternLength-1
                # entry price
                entryPrice = Close[entryCandleIdx]

                # ENTRY CONDITIONS

                ''' Check if the condition to close above pullback is True
                 If so check this and continue if not satisfied '''
                if closeAboveRed:
                    if entryPrice < Open[redCandleIdx]:
                        continue


                ''' If vwap is true i.e. price needs to be above it and the entryPrice
                is below vwap, then skip this pattern '''
                if vwap and entryPrice < day.vwap[entryCandleIdx]:
                    continue

                ''' First check if moving average is in the column list, if so check
                if the entry price is less than the moving average and skip if so '''
                priceAboveMABool = True
                if '-' in priceAboveMA:
                    priceAboveMABool = False
                    priceAboveMA = priceAboveMA.replace("-","")

                if priceAboveMA in df.columns:
                    if priceAboveMABool:
                        if entryPrice < day[priceAboveMA][entryCandleIdx]:
                            continue
                    else:
                        if entryPrice > day[priceAboveMA][entryCandleIdx]:
                            continue

                ''' First check if moving average is in the column list, if so check
                if the moving average is less than the moving average and skip if so '''
                if maAboveMAsplit[0] in df.columns and maAboveMAsplit[1] in df.columns:
                    if day[maAboveMAsplit[0]][entryCandleIdx] < day[maAboveMAsplit[1]][entryCandleIdx]:
                        continue

                ''' If we want to filter RSI and the RSI is greater than 80, skip '''
                if rsi and day.RSI14[entryCandleIdx] > 80:
                    continue

                ''' If entryVol true we want entry volume to be higher than pullback
                so if volume of Volume[redCandleIdx] is greater, then skip '''
                if entryVol and redCandleVol >= Volume[entryCandleIdx]:
                    continue

                # Define stop price
                stopPrice = redCandleLow - perShareAdjustment
                # Calculate risk for stop loss
                riskPerShare = round(entryPrice - stopPrice , 2)

                ''' Check if risk is too much per share '''
                if riskPerShare > (stopLimit + perShareAdjustment):
                    continue

                # Occasionally risk per share may be 0, skip this.
                if riskPerShare == 0: continue
                # Whether we wish to use accumulative pnl
                # Determine number of shares to buy
                riskAmount = (PnL * riskPercent)
                # Cap risk at 10,000
                if riskAmount > 10000:
                    riskAmount = 10000
                shareSize = round(riskAmount / riskPerShare, 2)
                # Define target price
                targetPrice = []
                if incremental:
                    targetPrice.append(entryPrice + (riskPerShare * ((profitTarget / 2) + 0.5)))
                targetPrice.append(entryPrice + (riskPerShare * profitTarget))
                # Update total trades
                Trades = Trades + 1
                # Update figure
                if drawFigures:
                    figure.AddMarker(day.index[entryCandleIdx], Close[entryCandleIdx], 'triangle-up', 'green', size=12)
                # Profit per pattern
                profit = 0
                # Iterate through candles whilst in trade
                for minIdx in range(entryCandleIdx+1,len(Close)):
                    if Low[minIdx] <= stopPrice:
                        '''Stopped out'''
                        loss = (-1 * ((riskPerShare * shareSize) + (costPerTrade * 2)))
                        PnL = PnL + loss
                        LossValue = LossValue + loss
                        # Have we lost everything
                        ''' Comment this out if you wish to fully evaluate '''
                        if PnL < 0:
                            Bust = Bust + 1
                        Stops = Stops + 1
                        # Update figure
                        if drawFigures:
                            figure.AddStopLine(day.index[entryCandleIdx], day.index[minIdx], stopPrice)
                            figure.AddMarker(day.index[minIdx], stopPrice, 'triangle-down', 'red', str(round(loss, 2)), size=12)
                        minIdx = len(Close)+1
                        break
                    elif minIdx >= len(Close)-2:
                        '''End of Day'''
                        # profit + current value of shares + (-1* cost of shares to buy plus the fees)
                        profit = (Close[minIdx] * shareSize) + (-1*((entryPrice * shareSize) + (costPerTrade * 2)))
                        PnL = PnL + profit
                        # Determine whether trade is up
                        if profit > 0:
                            ProfitValue = ProfitValue + profit
                        else:
                            LossValue = LossValue + profit
                        # Update figure
                        if drawFigures:
                            figure.AddStopLine(day.index[entryCandleIdx], day.index[minIdx], stopPrice)
                            figure.AddMarker(day.index[minIdx], Close[minIdx], 'triangle-down', 'red', str(round(profit, 2)), size=12)
                        # Set as EOD
                        EOD = EOD + 1
                        minIdx = len(Close)+1
                        break
                    elif Close[minIdx] >= targetPrice[0]:
                        '''Profit'''
                        if len(targetPrice) > 1:
                            ''' Incremental sell '''
                            incrementalSize = shareSize * 0.33
                            shareSize = shareSize - incrementalSize
                            profit = (targetPrice[0] * incrementalSize) + (-1* ((entryPrice * incrementalSize) + (costPerTrade)))
                            PnL = PnL + profit
                            ProfitValue = ProfitValue + profit
                            # Update figure
                            if drawFigures:
                                figure.AddMarker(day.index[minIdx], targetPrice[0], 'triangle-down', 'red', str(round(profit, 2)), size=8)
                            # Reduce array to 1 to move to next price
                            targetPrice = targetPrice[1:]
                            continue
                        else:
                            ''' Final sell '''
                            profit = (targetPrice[0] * shareSize) + (-1* ((entryPrice * shareSize) + (costPerTrade * 2)))
                            ProfitValue = ProfitValue + profit
                            PnL = PnL + profit
                            Profits = Profits + 1
                            # Update figure
                            if drawFigures:
                                figure.AddStopLine(day.index[entryCandleIdx], day.index[minIdx], stopPrice)
                                figure.AddMarker(day.index[minIdx], targetPrice[0], 'triangle-down', 'red', str(round(profit, 2)), size=12)
                            minIdx = len(Close)+1
                            break


        if drawFigures:
            figure.Save(destination + f"/figures/{symbol}_{str(round(PnL, 0))}_{str(random.randint(1000,9999))}.png")

    if Trades > 0:
        # Append to summary
        return (f"""{symbol},{Days},{incremental},{minVolume},{round(ProfitValue+LossValue,2)},{ProfitValue},{LossValue},{round((ProfitValue+LossValue) / Trades, 2)},{Trades},{round(Trades / Days,2)},{reset},{Profits},{Stops},{EOD},{Bust},{round(Profits / Trades, 2)},{riskPercent},{stopLimit},{' '.join(map(str, pattern))},{profitTarget},{priceAboveMA},{maAboveMA},{vwap},{rsi},{entryVol},{perShareAdjustment},{costPerTrade},{1 if (ProfitValue+LossValue) > 0 else 0}, {closeAboveRed}\n""")
