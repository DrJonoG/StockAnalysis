
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

import pandas as pd
import numpy as np
import os
import mplfinance as mpf
import configparser
from helpers import ConfigParser
from .TradeLogger import OutputColumns, TradeDataFrame

# Surpress warnings
pd.options.mode.chained_assignment = None

class PullbackToMA:
    def __init__(self, configPath):
        # Load the configuration file
        parser = configparser.RawConfigParser()
        # Ensure original case is kept
        parser.optionxform = str
        parser.read(configPath)
        # Self object variables
        self.__dict__.update(dict(ConfigParser(parser.items("PullbackToMA"))))
        # Create destination folder
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)
        # Output columns
        self.outputColumns = OutputColumns()
        self.outputColumns.Initialise()
        # Trade Logger
        self.tradeMonitor = TradeDataFrame()
        self.tradeMonitor.Initialise()

    def GroupDF(self, df):
        # To datetime
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        # Update index to allow for splitting of trends
        self.df = df.reset_index()
        # Check if smaller ma is above larger, if not, remove from list
        if self.movingAveragePB and self.movingAverageMax:
            self.df = self.df[(self.df[str(self.movingAveragePB) + self.movingAverageType] > self.df[str(self.movingAverageMax) + self.movingAverageType]) & (self.df[str(self.movingAverageMax) + self.movingAverageType] > 0)].set_index('index')#.drop(columns=['Unnamed: 0'])
        elif self.movingAveragePB and not self.movingAverageMax:
            self.df = self.df[(self.df.close > self.df[str(self.movingAveragePB) + self.movingAverageType]) & (self.df[str(self.movingAveragePB) + self.movingAverageType] > 0)].set_index('index')
        # group by date
        dfGrouped = self.df.groupby([self.df['Datetime'].dt.date], group_keys=False)#.agg(['mean', 'min', 'max'])#.apply(self.DayEval)
        print(dfGrouped['Datetime'])
        return dfGrouped


    def SaveDf(self, df, filename):
        # If file exists append, else create
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False)
        else:
            df.to_csv(filename, index=True)


    def Update(self, tradeDictionary, exit, sym):
        # Data series
        series = {
            'Entry Datetime': tradeDictionary['entryCandle'].Datetime,
            'Exit Datetime': exit,
            'Sym': sym,
            'Position Size': round(tradeDictionary['entrySize'],0),
            'Final size': tradeDictionary['remainingPosition'],
            'Entry Price': round(tradeDictionary['entryCandle'].close,2),
            'Original Stop': round(tradeDictionary['originalStop'], 2),
            'Adjusted Stop': round(tradeDictionary['stopTarget'],2),
            'Profit Target (1)': round(tradeDictionary['profitTargets'][0],2),
            'Profit Target (2)': round(tradeDictionary['profitTargets'][1],2),
            'Profit Target (3)': round(tradeDictionary['profitTargets'][2],2),
            'Profit (1)': round(tradeDictionary['profits'][0],2),
            'Profit (2)': round(tradeDictionary['profits'][1],2),
            'Profit (3)': round(tradeDictionary['profits'][2],2),
            'Exit Price': round(tradeDictionary['exitPrice'], 2),
            'Exit PnL': round(tradeDictionary['exitPNL'],2),
            'PnL': round(tradeDictionary['profits'][0]+tradeDictionary['profits'][1]+tradeDictionary['profits'][2]+tradeDictionary['exitPNL'], 2),
            'Total Bars': tradeDictionary['barCount'],
            'Exit Type': tradeDictionary['exitType']
        }
        self.dfTrades = self.dfTrades.append(series, ignore_index=True)


    def VariableDictionary(self):
        fig = {
            # Figure variables
            'upMarkers':  [],
            'downMarkers':  [],
            'verticalLines':  []
        }

        return fig


    def DrawFigure(self, fig, tradeDictionary, group, sym):
        if len(fig['downMarkers']) != len(group):
            fig['upMarkers'].append(np.nan)
            fig['downMarkers'].append(np.nan)
        #if len(fig['upMarkers']) == len(fig['downMarkers']) and len(fig['upMarkers']) == len(group):
        group_copy = group.set_index(pd.DatetimeIndex(group['Datetime'])).copy()

        up_plot = mpf.make_addplot(fig['upMarkers'], type='scatter', marker='^', color='g', markersize=100, panel=0)
        down_plot = mpf.make_addplot(fig['downMarkers'], type='scatter', marker='v', color='r', markersize=100, panel=0)
        plots = [up_plot, down_plot,  mpf.make_addplot(group_copy['20EMA'])]
        mc = mpf.make_marketcolors(up='green', down='red', edge='black')
        s = mpf.make_mpf_style(marketcolors=mc, y_on_right=True)

        mpf.plot(
            group_copy,
            title= sym + ": " + str(tradeDictionary['entryCandle'].Datetime) + ". PnL: $" + str(round(tradeDictionary['profits'][0]+tradeDictionary['profits'][1]+tradeDictionary['profits'][2]+tradeDictionary['exitPNL'],2)),
            ylabel='Price ($)',
            type='candle',
            #style='charles',
            hlines=dict(hlines=[tradeDictionary['profitTargets'][0],tradeDictionary['profitTargets'][1],tradeDictionary['originalStop']],colors=['g','g','r'],linestyle='-.'),
            vlines=dict(vlines=[fig['verticalLines']], colors=['b'], alpha=0.35, linewidths=20),
            addplot=plots,
            figsize =(20,20),
            style='yahoo',
            #tight_layout=True,
            savefig="D:/StockData/5Minutes/processed/Evaluation/PullBackMA/figures/" + sym + "_" + str(tradeDictionary['entryCandle'].Datetime).replace(":","") + ".png"
        )

    def InTrade(self, fig, candle, time):
        inTrade = True
        # Number of bars in trade
        self.tradeMonitor.Set(self.tradeMonitor.Get('barCount') + 1, 'barCount')
        # check to see if market is closing or if we reach our stop loss target:
        if time >= self.closeTime or candle.low <= self.tradeMonitor.Get('stopTarget'):
            fig['downMarkers'][-1] = candle.close
            self.tradeMonitor.Set(candle.close, 'exitPrice')
            self.tradeMonitor.Set((candle.close * self.tradeMonitor.Get('remainingPosition')) - (self.tradeMonitor.Get('entryCandle').close * self.tradeMonitor.Get('remainingPosition')), 'exitPNL')

            if time >= self.closeTime:
                self.tradeMonitor.Set("Market Close", 'exitType')
            else:
                self.tradeMonitor.Set("Stop Target", 'exitType')
            inTrade = False
        elif candle.close >= self.tradeMonitor.Get('profitTargets')[self.tradeMonitor.Get('currentTarget')]:
            fig['downMarkers'][-1] = candle.close
            # Quantity
            self.tradeMonitor.Set(self.tradeMonitor.Get('entrySize')*self.profitSellSize[self.tradeMonitor.Get('currentTarget')], 'sellQty')
            self.tradeMonitor.Set(self.tradeMonitor.Get('remainingPosition') -  self.tradeMonitor.Get('sellQty'), 'remainingPosition')
            # Adjust stop to entry
            self.tradeMonitor.Set(self.tradeMonitor.Get('entryCandle').close, 'stopTarget')
            # Adjust tradeDictionary['profits']
            """
            Todo set up the profit targets

            """
            #self.tradeMonitor.Set((candle.close * self.tradeMonitor.Get('sellQty')) - (self.tradeMonitor.Get('entryCandle').close * self.tradeMonitor.Get('sellQty')), 'profits'[tradeDictionary['currentTarget']])
            #tradeDictionary['profits'][tradeDictionary['currentTarget']] = (candle.close * tradeDictionary['sellQty']) - (tradeDictionary['entryCandle'].close * tradeDictionary['sellQty'])
            # If this was the final target then exit
            if self.tradeMonitor.Get('currentTarget') == 2:
                self.tradeMonitor.Set(candle.close, 'exitPrice')
                self.tradeMonitor.Set("Profit Target", 'exitType')
                self.tradeMonitor.Set(0, 'remainingPosition')
                inTrade = False

            self.tradeMonitor.Set(self.tradeMonitor.Get('currentTarget') + 1, 'currentTarget')

        return inTrade, fig

    def IteratorFunction(self, df, sym):
        dfGrouped = self.GroupDF(df)
        #Iterate through each group
        for name, group in dfGrouped:
            # variables
            fig = self.VariableDictionary()
            self.tradeMonitor.Reset()
            inTrade = False
            touchedMA = False
            touchedMACount = 0
            # Iterate through the rows of each group
            groupStartIndex = 0
            for i in range(0, len(group)):
                #
                fig['upMarkers'].append(np.nan)
                fig['downMarkers'].append(np.nan)
                # Get tick data
                candle = group.iloc[i]
                time = candle.Datetime.time()
                # Allow for x candles between touching ma and getting into a trade before cancelling
                if touchedMA and not inTrade:
                    touchedMACount += 1
                    if touchedMACount >= 6:
                        touchedMA = False
                        touchedMACount = 0
                ##### Check if we have not yet fig['entered'] a trade or gone close to the MA
                if not inTrade and not touchedMA and time < self.finalEntry and time > self.firstEntry and candle.Candle == -1:
                    # If we are not in a trade, and havent found our trigger candle
                    if abs((candle.close - candle[str(self.movingAveragePB) + self.movingAverageType]) / float(candle.close)) <= self.withinRange:
                        # Within range of the ma
                        touchedMA = True
                        self.tradeMonitor.Set(candle,'triggerCandle')
                        # Define our stop loss position
                        self.tradeMonitor.Set(candle.low * .95,'stopTarget')
                        self.tradeMonitor.Set(self.tradeMonitor.Get('stopTarget'),'originalStop')
                        # Define fig['verticalLines']
                        fig['verticalLines'] = candle.Datetime
                elif not inTrade and touchedMA and time < self.finalEntry and time > self.firstEntry and candle.close > self.tradeMonitor.Get('triggerCandle').open and candle.Candle == 1 and candle.close > candle[str(self.movingAveragePB) + self.movingAverageType]:
                    ##### Check if we are not in a trade and have touched the target ma
                    # The candle closed above the trigger and is a bull candle (long entry) and is now above the moving average
                    inTrade = True
                    self.tradeMonitor.Set(candle,'entryCandle')
                    # Determine size and round to whole number, calculate cost of position. The maximum risk divided by the risk per trade
                    self.tradeMonitor.Set(round(self.maxRisk / (self.tradeMonitor.Get('entryCandle').close - self.tradeMonitor.Get('stopTarget')),0), 'entrySize')
                    self.tradeMonitor.Set(self.tradeMonitor.Get('entrySize'),'remainingPosition')
                    self.tradeMonitor.Set(self.tradeMonitor.Get('entrySize') * self.tradeMonitor.Get('entryCandle').close,'totalCost')
                    # Define 3 stop targets
                    self.tradeMonitor.Set(self.tradeMonitor.Get('entryCandle').close + ((self.tradeMonitor.Get('entryCandle').close - self.tradeMonitor.Get('stopTarget')) * self.profitMultiplyer),'profitTargets')
                    # Updates for figure
                    fig['upMarkers'][-1] = candle.close
                elif inTrade:
                    inTrade, fig = self.InTrade(fig, candle, time)
                    if not inTrade:
                        fig['downMarkers'][-1] = candle.close
                        self.Update(tradeDictionary, candle.Datetime, sym)
                        # Draw figure
                        if self.drawFigures: self.DrawFigure(fig, tradeDictionary, group[groupStartIndex:i+1], sym)
                        # Reset variables
                        fig = self.VariableDictionary()
                        self.tradeMonitor.Reset()
                        groupStartIndex = i
                        touchedMA = False
                        touchedMACount = 0


    def Run(self, df, sym):
        self.IteratorFunction(df, sym)
        #iterator(overview, folder, start_date, end_date, trading_start, trading_stop, self.IteratorFunction)
        #self.dfTrades = self.dfTrades.reindex(self.dfTrades.columns, axis=1)
        #self.SaveDf(self.dfTrades, self.destination + str(self.movingAveragePB) + "_Pullback.csv")
