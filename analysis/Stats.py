
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

# analysis of the impact of the previous day close, to the current day based on the opening bar
import numpy as np
import os
import time
from datetime import datetime, timedelta

import pandas as pd
from helpers import csvToPandas

"""
=> General stats from data such as ATR, Avg Vol etc.
"""

def stockDirection(candle):
    return sum(candle)/len(candle)

def MinMaxStats(df):
    minLow = min(df.low)
    maxHigh = max(df.high)
    avgVol = sum(df.volume) / len(df.volume)
    return minLow, maxHigh, avgVol

def Overview(df, frequency):
    # Group by blocks of frequency minutes
    overview = df[(df.volume > 0) & (df.index.dayofweek<5)].groupby([pd.Grouper(freq=frequency)]).apply(lambda s: pd.Series({
        'volAverage': 0 if len(s['volume']) == 0 else round(sum(s['volume']) / len(s['volume']),0),
        'direction': 0 if len(s['Candle']) == 0 else stockDirection(s['Candle']),
        'ATR': 0 if len(s['high']) == 0 else sum(s['high'] - s['low']) / len(s['high'])
    }))
    # Then group multiple days
    overview = overview.between_time('04:30:00', '20:00:00')
    overview = overview.groupby(overview.index.time).apply(lambda s: pd.Series({
        'volAverage': 0 if len(s['volAverage']) == 0 else round(sum(s['volAverage']) / len(s['volAverage']),0),
        'direction': 0 if len(s['direction']) == 0 else stockDirection(s['direction']),
        'ATR': 0 if len(s['ATR']) == 0 else sum(s['ATR']) / len(s['ATR'])
    }))

    overview = overview.fillna(0)

    # Group by prices in blocks of $0.10
    pricing = df[df.volume > 0].groupby([np.around(df.close, 1)]).apply(lambda s: pd.Series({
        'minuteCount': len(s['close']),
        'volTotal': sum(s['volume']),
        'volAverage': 0 if len(s['close']) == 0 else round(sum(s['volume']) / len(s['close']),0),
        'ATR': 0 if len(s['high']) == 0 else sum(s['high'] - s['low']) / len(s['high'])
    }))

    return overview, pricing,

def Analyse(symbol, source, destination, marketOnly=True):
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
    # Load DF
    df = csvToPandas(source + symbol)

    # month processing
    monthStart = datetime.today() - timedelta(days = 28)
    monthDF = df[df.index >= monthStart]
    if len(monthDF.index) > 2:
        monthStats = MinMaxStats(monthDF)
        monthOverview, monthPricing = Overview(monthDF, '5Min')
        monthOverview.to_csv(destination + symbol.replace('.csv', '_m_overview.csv'), mode='w')
        monthPricing.to_csv(destination + symbol.replace('.csv', '_m_pricing.csv'), mode='w')

    # week processing
    weekStart = datetime.today() - timedelta(days = 7)
    weekDF = df[df.index >= weekStart]
    if len(weekDF.index) > 2:
        weekStats = MinMaxStats(weekDF)
        weekOverview, weekPricing = Overview(weekDF, '5Min')
        weekOverview.to_csv(destination + symbol.replace('.csv', '_w_overview.csv'), mode='w')
        weekPricing.to_csv(destination + symbol.replace('.csv', '_w_pricing.csv'), mode='w')
