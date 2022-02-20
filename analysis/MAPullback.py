
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
import datetime
import numpy as np
import pandas as pd
import matplotlib.lines as lines
import matplotlib.pyplot as plt
import financialanalysis as fa
from core import Figure
from pathlib import Path
from sklearn.linear_model import LinearRegression

from helpers import csvToPandas, PrintProgressBar

def CalculateSlope(x,y):
    ## Prepare data
    X = x.values.astype(np.int64) // 10 ** 9 # for example, 2020-07-01 becomes 2020.49589041
    X = np.array(X) # convert list to a numpy array

    X -= X[0] # make it begin with 0.
    X = X[::,None] # convert row vector to column vector (just column vector is acceptable)
    y = y[::,None] # row vector to column vector (just column vector is acceptable)

    ## Apply linear regression
    reg = LinearRegression().fit(X, y) # start regression (X and y are both column vectors)
    slope = reg.coef_[0][0] # vslope of line (get first element from 2D array)
    intercept = reg.intercept_[0] # intercept with the y-axis (get first element from 1D array)

    fittedline = slope*X + intercept # generate prediction line (y=ax+b)
    fittedline = fittedline.flatten() # column vetor to row vector (just for displaying data)

    return slope, intercept, fittedline

def Analyse(symbol, source, destination, marketOnly=True):
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
    """

    # Load DF
    if not os.path.exists(source + symbol): return
    df = csvToPandas(source + symbol)

    # Check index is correct format
    if type(df.index) != pd.core.indexes.datetimes.DatetimeIndex: return

    # Filter out symbols that are penny stocks or too high in value
    if df.close.min() > 80 or df.close.max() < 5: return

    # Open market only
    if marketOnly:
        df = df[(df.index.hour >= 8) & (df.index.hour < 16)]

    # Filter out data over a year old
    # Older dates have less signifcance as markets change
    df = df[df.index > '2021-01-01']

    # log file:
    fileName = 'OriginalCodeMaxBelow2Slope0to3SmallPT.csv'
    if not os.path.exists(destination + fileName):
        with open(destination + fileName, "w") as f:
            f.write("Symbol,ProfitTarget,StopPadding,SlopeValue,SlopeLookBackBars,fastAboveFor,MaxBelowFor,Win%,Profit,Wins,Losses,AvgBars,fastMA,slowMA,Above50MA,FastTrendAboveSlow\n")
    f = open(destination + fileName, 'a')
    """ Parameters """
    # Stop details
    stopPadding = 0.03
    risk = 200
    # Profit details
    profitTargetMultiplier = 1.2
    # Filter slope, should we only trade on certain slopes, if so, which
    # Slope value specifies the slope should be greater than slopeValue[0] and less than slopeValue[1]
    slopeValueArr = [[0,3]]#,[0,5],[-5,5],[-30,30]]
    # Slope look back, how many bars the linear regression is calculated on
    slopeLookBackArr = [20]
    # Maximum number of bars below the slow MA before we stop looking for an entry
    maxBelowArr = [3]
    # Number of bars the fast must be above the slow before we look for entry
    fastAboveArr = [10]
    # The columns to use for cross over entry
    fastMAArr = ["3EMA"]
    slowMAArr = ["10EMA"]
    """ End Parameters """
    for slopeValue in slopeValueArr:
        for fastAbove in fastAboveArr:
            for slopeLookBack in slopeLookBackArr:
                for maxBelow in maxBelowArr:
                    for fastMACol in fastMAArr:
                        for slowMACol in slowMAArr:
                            # Total counters
                            totalWins = 0
                            totalLosses = 0
                            totalBars = 0
                            # Iterate through each day
                            for idx, day in df.groupby(df.index.date):
                                # Pandas to numpy
                                Volume = day.volume.to_numpy()

                                # Check if any entries
                                if Volume.shape[0] < 1:
                                    continue
                                # check if average volume below min volume
                                if sum(Volume) < 5000000:
                                    continue

                                # Convert columns to numpy
                                Date = day.index
                                CandleDir = day.Candle.to_numpy()
                                Close = day.close.to_numpy()
                                Open = day.open.to_numpy()
                                Low = day.low.to_numpy()
                                High = day.high.to_numpy()
                                fastMA = day[fastMACol].to_numpy()
                                slowMA = day[slowMACol].to_numpy()
                                trendFast = day['50EMA'].to_numpy()
                                trendSlow = day['100EMA'].to_numpy()
                                # Create figure
                                figure = Figure.Figure()
                                figure.CandleStick(day)
                                figure.TextConfig(chartTitle=f"{symbol} : {idx}")
                                figure.AddLine(day, "50EMA", "yellow", "50 EMA",2)
                                figure.AddLine(day, "100EMA", "green", "100 EMA",3)
                                figure.AddLine(day, slowMACol, "red", slowMACol)
                                figure.AddLine(day, fastMACol, "yellow", fastMACol)
                                # Counters
                                fastAboveSlow = 0
                                fastCrossBelow = 0
                                fastCrossAbove = 0
                                # Price info
                                profitTarget = 0
                                stopLoss = 0
                                # Whether trade was made
                                traded = False
                                #for i, date in enumerate(Date):
                                # Entry id
                                entryID = 0
                                # Counter
                                i = -1
                                while i < len(Date)-1:
                                    i += 1
                                    if fastAboveSlow >= fastAbove:
                                        if fastCrossBelow > maxBelow:
                                            # If been under the slow for more than maxBelow ticks, trend has changed so exit
                                            fastCrossAbove = 0
                                            fastCrossBelow = 0
                                            fastAboveSlow = 0
                                            continue
                                        # Look for entry
                                        if fastCrossAbove > 0:
                                            # Check if MA condition satisied if not stop looking for entry
                                            if High[i] >= profitTarget:
                                                totalWins += 1
                                                # Profit target met, exit trade
                                                fastCrossAbove = 0
                                                fastAboveSlow = 0
                                                fastCrossBelow = 0
                                                # Add exit to figure
                                                figure.AddMarker(Date[i], profitTarget, 'triangle-down', 'red', str(profitTarget) + ' (P)', size=16)
                                                i = entryID
                                            elif Low[i] > stopLoss:
                                                # Remain in trade
                                                totalBars += 1
                                                fastCrossAbove += 1
                                            elif Low[i] <= stopLoss:
                                                totalLosses += 1
                                                # Exit trade due to stop
                                                fastCrossAbove = 0
                                                fastAboveSlow = 0
                                                # Add exit to figure
                                                figure.AddMarker(Date[i], stopLoss, 'triangle-down', 'red', str(stopLoss) + ' (L)', size=16)
                                                i = entryID
                                            else:
                                                # Exit trade for other reason (not stop or profit)
                                                fastCrossAbove = 0
                                                fastAboveSlow = 0
                                                # Add exit to figure
                                                figure.AddMarker(Date[i], Close[i], 'triangle-down', 'red', str(Close[i]), size=6)
                                        elif fastMA[i] <= slowMA[i]:
                                            # Fast is below slow, increment count
                                            fastCrossBelow += 1
                                        elif fastCrossBelow > 0:
                                            # Fast MA is above slowMA so enter if criteria met
                                            slopeDist = (0 if i < slopeLookBack else i - slopeLookBack)
                                            slope, intercept, fittedLine = CalculateSlope(Date[slopeDist:i],Close[slopeDist:i])
                                            slope = slope*10000
                                            # Additional criteria before entering
                                            if slope < slopeValue[0] or slope > slopeValue[1]:
                                                fastCrossBelow = 0
                                                # Do not enter trade: 1. after 2pm, 2. if stop is > $0.50, 3. If bar volume less than minimum specified
                                            elif Date[i].hour > 14 or (Date[i].hour == 9 and Date[i].minute > 29 and  Date[i].minute < 46)  or ((Close[i] - min(Low[i-fastCrossBelow:i])) + stopPadding) > 0.50 or ((Close[i] - min(Low[i-fastCrossBelow:i])) + stopPadding < 0.07) or Volume[i] < 20000 or ((np.average(Volume[i-fastCrossBelow:i])) * 1.2 > Volume[i]):
                                                    fastCrossBelow = 0
                                            else:
                                                entryID = i
                                                #figure.AddSlope(Date[slopeDist], Date[i-1], fittedLine[0], fittedLine[-1], slope)
                                                profitTarget = round(Close[i] + ((Close[i] - min(Low[i-fastCrossBelow:i]) + stopPadding) * profitTargetMultiplier),2)
                                                stopLoss = round(min(Low[i-fastCrossBelow:i]) - stopPadding,2)

                                                # Add entry to figure
                                                totalRiskValue = round((Close[i] - min(Low[i-fastCrossBelow:i])) + stopPadding, 2)
                                                figure.AddMarker(Date[i], Close[i], 'triangle-up', 'green', str(Close[i]), size=16)
                                                figure.AddStopLine(Date[i], Date[i-fastCrossBelow], stopLoss, str(stopLoss) + " " + str(totalRiskValue))

                                                traded = True
                                                # Enter trade
                                                fastCrossAbove = 1
                                                fastCrossBelow = 0
                                                totalBars += 1

                                                #elif ((fastMA[i] >= slowMA[i]) & (trendFast[i] > trendSlow[i])):
                                    elif (fastMA[i] >= slowMA[i]) and (trendFast[i] > trendSlow[i]):# and (slowMA[i] < trendFast[i]):
                                        fastAboveSlow += 1
                                    else:
                                        fastAboveSlow = 0

                                #if traded and random.randint(0, 10) == 3:
                                #    figure.Save(destination + f"/figures3/FastTrendAboveSlowTrendPriceAsFastMA_{symbol}_{str(idx)}.png")

                            totalTrades = totalWins+totalLosses
                            if totalTrades > 0:
                                f.write(f"{symbol},{profitTargetMultiplier},{stopPadding},> {str(slopeValue[0])} & < {str(slopeValue[1])},{slopeLookBack},{fastAbove},{maxBelow},{round((totalWins/totalTrades)*100,2)},{(totalWins*(risk*profitTargetMultiplier))-(totalLosses*risk)},{totalWins},{totalLosses},{round(totalBars/totalTrades,2)},{fastMACol},{slowMACol},NA,True\n")
                            # Above50MA,FastTrendAboveSlow
def Summary(directory, destination):
    # Load all files
    if not os.path.exists(directory + 'Merged.csv'):
        files = list(Path(directory).rglob('*.csv'))
        masterDF = pd.concat((pd.read_csv(f, header = 0) for f in files))
        masterDF.to_csv(directory + 'Merged.csv', index=False)
    else:
        # Load master
        masterDF = pd.read_csv(directory + 'Merged.csv', index_col = 0)

    # summary file:
    fileName = 'SummaryFastMAPB.csv'
    masterDF  = masterDF.fillna(0)
    masterDFGrp = masterDF.groupby(['ProfitTarget','StopPadding','SlopeValue','SlopeLookBackBars','fastAboveFor','MaxBelowFor', 'fastMA','slowMA']).agg({'Profit':'sum','Wins':'sum','Losses':'sum','AvgBars':'mean'})

    masterDFGrp['AvgBars'] = round(masterDFGrp['AvgBars'],2)
    masterDFGrp['Trades'] = masterDFGrp['Wins'] + masterDFGrp['Losses']
    masterDFGrp['Cost'] = masterDFGrp['Trades'] * 10
    masterDFGrp['Win%'] = round(masterDFGrp['Wins'] / masterDFGrp['Trades'],4)
    masterDFGrp.to_csv(destination + fileName)

    fileName = 'SummaryFastMAPB_2.csv'

    masterDFSubGrp = masterDF.groupby(['fastMA']).agg({'Profit':'sum','Wins':'sum','Losses':'sum','AvgBars':'mean'})
    masterDFSubGrp['AvgBars'] = round(masterDFSubGrp['AvgBars'],2)
    masterDFSubGrp['Trades'] = masterDFSubGrp['Wins'] + masterDFSubGrp['Losses']
    masterDFSubGrp['Cost'] = masterDFSubGrp['Trades'] * 10
    masterDFSubGrp['Win%'] = round(masterDFSubGrp['Wins'] / masterDFSubGrp['Trades'],4)
    print(masterDFSubGrp)
