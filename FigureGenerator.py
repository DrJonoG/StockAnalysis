
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
import glob
import configparser
import random as rnd
import cufflinks as cf
import mplfinance as mpf
import plotly.figure_factory
import core.GetData as getData
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mplfinance.original_flavor import candlestick_ohlc
from helpers import SymbolIterator, csvToPandas

# Load the file and strip out unwanted data
def loadFile(filepath):
    df = csvToPandas(filepath)
    # Open market only
    df = df[(df.index.hour >= 8) & (df.index.hour < 16)]
    # Filter out data over a year old
    # Older dates have less signifcance as markets change
    df = df[df.index > '2021-01-01']

    return df

def createFigure(chartTitle, day,xAxis):
    #chartTitle = fileName + '_' + str(idx) + '_1Min'
    MA10 = mpf.make_addplot(day['10EMA'].to_numpy(),type='line', width=0.3, color='darkblue')
    MA20 = mpf.make_addplot(day['20EMA'].to_numpy(),type='line', width=0.8, color='deepskyblue')
    MA50 = mpf.make_addplot(day['50EMA'].to_numpy(),type='line', width=2, color='royalblue')
    MA100 = mpf.make_addplot(day['100EMA'].to_numpy(),type='line', width=5, color='darkblue')
    fig, axlist = mpf.plot(day,
        type='candle',
        style='yahoo',
        figsize=(60,30),
        volume=True,
        tight_layout=True,
        addplot=[MA10, MA20, MA50,MA100],
        title= chartTitle,
        ylabel='Price',
        xrotation=45,
        ylabel_lower='Shares \nTraded',
        returnfig=True
    )
    ytick = round(day.close.max()/400, 2);
    axlist[0].xaxis.set_major_locator(ticker.MultipleLocator(xAxis))
    axlist[0].yaxis.set_major_locator(ticker.IndexLocator(base=ytick, offset=0) );

    return fig, axlist

oneMinPath = 'H:/Indicators/1m/'
twoMinPath = 'H:/Indicators/2m/'
fiveMinPath = 'H:/Indicators/5m/'

for filepath in glob.glob(oneMinPath + '*.csv'):
    fileName = os.path.basename(filepath)
    if  fileName[0] == 'B' or fileName[0] == 'C' or fileName[0] == 'D' or fileName[0] == 'E' or fileName[0] == 'F' or fileName[0] == 'G':
        continue
    print(fileName)
    try:
        minDF = loadFile(filepath)
        # Checker average price isn't too small or large
        avgPrice = minDF['close'].mean()
        if avgPrice < 5 or avgPrice > 80:
            continue
        # Load remaining timeframes if price is satisied
        twoDF = loadFile(twoMinPath + fileName)
        fiveDF = loadFile(fiveMinPath + fileName)
    except Exception:
        print("Error on " + filePath)

    # Group minute data
    # Iterate through each day
    for idx, day in minDF.groupby(minDF.index.date):
        # Pandas to numpy
        Volume = day.volume.to_numpy()
        # Check if any entries
        if Volume.shape[0] < 1:
            continue
        # check if average volume below min volume
        if sum(Volume) < 10000000:
            continue
        # Select corresponding timeframe data
        grpTwoDF = twoDF[(twoDF.index.normalize() == day.index[0].normalize())]
        grpFiveDF = fiveDF[(fiveDF.index.normalize() == day.index[0].normalize())]
        # Ensure corresponding time frames exist for date
        if grpTwoDF.shape[0] == 0 or grpFiveDF.shape[0] == 0:
            continue

        if rnd.randint(0,15) == 5:
            chartTitle = fileName + '_' + str(idx)
            randomNumber = str(rnd.randint(0,10))

            fig, axis = createFigure(chartTitle + '_1Min', day, 10)
            fig.savefig('H:/Charts/' + randomNumber + '_' + chartTitle + '_1Min' + '.jpg', bbox_inches='tight')
            plt.close(fig)

            fig2, axis2 = createFigure(chartTitle + '_2Min', grpTwoDF, 5)
            fig2.savefig('H:/Charts/' + randomNumber + '_' + chartTitle + '_2Min' + '.jpg', bbox_inches='tight')
            plt.close(fig2)

            fig5, axis5 = createFigure(chartTitle + '_5Min', grpFiveDF, 1)
            fig5.savefig('H:/Charts/' + randomNumber + '_' + chartTitle + '_5Min' + '.jpg', bbox_inches='tight')
            plt.close(fig5)

            plt.clf()
