
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

# Important # NOTE:
#
# I do not take any responsbility for the use of the hotkeys, all generated hotkeys should be fully tested prior to use
# in a simulated environment
#

from PIL import Image, ImageDraw, ImageFont
import pandas as pd

class HotKeys:
    def __init__(self):
        self.configDF = pd.DataFrame(columns=['Key','Name','Command'])

    def AddHotkey(self, key, name, command):
        self.configDF = self.configDF.append({
            'Key': key,
            'Name': name,
            'Command': command
        }, ignore_index=True)

    def StopPosition(self, keys, amount, focus, clear, name, send):
        for i in range(0, len(amount)):
            command = '%s%sROUTE=STOP;StopType=Market;StopPrice=Ask-%s;Share=Pos;TIF=DAY+;SELL=%s;' % (focus, clear, str(amount[i]), send)
            self.AddHotkey(keys[i], name + str(amount[i]) + '%.', command)

    def CoverShort(self, keys, percent, focus, clear, name, send, stop=False):
        if len(keys) != len(percent):
            return "Error: Length must be the same."
        adjustStop = ''
        if stop:
            adjustStop = 'ROUTE=STOP;StopType=Market;StopPrice=AvgCost;Share=Pos-share;TIF=GTC;BUY=SEND'
        for i in range(0, len(percent)):
            command = '%s%sROUTE=LIMIT;Price=ASK+0.03;Price=Round2;Share=Pos*%s;TIF=DAY+;BUY=%s;' % (focus, clear, str(percent[i]), send)
            self.AddHotkey(keys[i], name + str(percent[i]*100) + '%.', command)

    def SellPosition(self, keys, percent, focus, clear, name, send, stop=False):
        if len(keys) != len(percent):
            return "Error: Length must be the same."
        adjustStop = ''
        if stop:
            adjustStop = 'ROUTE=STOP;StopType=Market;StopPrice=AvgCost;Share=Pos-share;TIF=DAY;SELL=SEND'
        for i in range(0, len(percent)):
            command = '%s%sROUTE=LIMIT;Price=BID-0.03;Price=Round2;Share=Pos*%s;TIF=DAY;SELL=%s;%s' % (focus, clear, str(percent[i]), send, adjustStop)
            self.AddHotkey(keys[i], name + str(percent[i]*100) + '%.', command)

    def TradeHotkeysRisk(self, longKeys, shortKeys, totalRisk, riskAmount, focus, slippage, send):
        for i in range(0, len(longKeys)):
            buyCommand = '%sROUTE=SMRTL;Share=%s/%s;Price=Ask+%s;StopPrice=Ask-%s;TIF=DAY+;BUY=%s;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:StopPrice ACT:SELL QTY:POS TIF:DAY+' % (focus, totalRisk, riskAmount[i], slippage, riskAmount[i], send)
            self.AddHotkey(longKeys[i], 'Risk %s' % str(riskAmount[i]), buyCommand)

    def TradeHotkeysQuantity(self, longKeys, shortKeys, tradeQty, focus, slippage, send):
        for i in range(0, 10):
            if len(longKeys) >= i:
                buyCommand = '%sROUTE=SMRTL;Price=Ask;Share=%s;Price=%s;StopPrice=Ask-Price;Price=Ask+%s;TIF=DAY+;BUY=%s;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:StopPrice ACT:SELL QTY:POS TIF:DAY+' % (focus, str(tradeQty[i]), str(round(riskValue/tradeQty[i], 2)), slippage, send)
                self.AddHotkey(longKeys[i], 'Long %s' % str(tradeQty[i]), buyCommand)
            if len(shortKeys) >= i:
                sellCommand = '%sROUTE=SMRTL;Price=Ask;Share=%s;Price=%s;StopPrice=Ask+Price;Price=Ask-%s;TIF=DAY+;SELL=%s;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:StopPrice ACT:BUY QTY:POS TIF:DAY+' % (focus, str(tradeQty[i]), str(round(riskValue/tradeQty[i], 2)), slippage, send)
                self.AddHotkey(shortKeys[i], 'Short %s' % str(tradeQty[i]), sellCommand)

    def Save(self, path):
        self.configDF = self.configDF.sort_values(by='Name', ascending=True, key=lambda col: col.str.lower())
        # Path to das trader directory, do not overwrite original hotkey file.
        with open(path, 'w') as f:
            for index, row in self.configDF.iterrows():
                f.write(str(row['Key']) + ':' + row['Name'] + ':' + row['Command'] + '\n')


if __name__ == '__main__':
    # Adjust your risk value here to automatically increase the position sizes
    accountSize = 10000
    riskPercent = 0.02
    riskValue = accountSize * riskPercent
    focus = 'FocusWindow Level2;' #'FocusWindow Level2;'
    clear = 'CXL ALLSYMB;'
    send = 'Send'
    slippage = '0.03'
    # risk
    stopKeys = ['Shift+v','Shift+b','Shift+n','Shift+m']
    stopValues = [0.1, 0.2, 0.3, 0.5]
    # long and short hotkeys
    longKeys = ['Ctrl+1','Ctrl+2','Ctrl+3','Ctrl+4','Ctrl+5','Ctrl+6','Ctrl+7','Ctrl+8','Ctrl+9','Ctrl+0']
    shortKeys = ['F1', 'F2','F3', 'F4','F5', 'F6','F7', 'F8','F9', 'F10']
    tradeQty = [100, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 5000]
    # Long risk keys
    longKeysRisk = ['Shift+1','Shift+2','Shift+3','Shift+4','Shift+5','Shift+6','Shift+7','Shift+8','Shift+9','Shift+0']
    riskAmount = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1.00]
    # Long risk with half risk value
    longKeysHalfRisk = ['Ctrl+Shift+1','Ctrl+Shift+2','Ctrl+Shift+3','Ctrl+Shift+4','Ctrl+Shift+5','Ctrl+Shift+6']
    halfRiskAmount = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    # Sell and cover positions
    coverKeys = ['Delete','End', 'PageDown']
    sellKeys = ['Insert','Home','PageUp']
    sellKeysStop = ['Ctrl+Insert','Ctrl+Home','Ctrl+PageUp']
    coversKeysStop = ['Ctrl+Delete','Ctrl+End', 'Ctrl+PageDown']
    sellPercent = [.33, .5, 1]
    # Initialise hotkeys config df
    hotkey = HotKeys()
    # risk
    #hotkey.StopPosition(stopKeys, stopValues, focus, clear, 'Adjust Stop ', send)
    # trade
    #hotkey.TradeHotkeysRisk(longKeysRisk, shortKeys, riskValue, riskAmount, focus, slippage, send)
    #hotkey.TradeHotkeysRisk(longKeysHalfRisk, shortKeys, (riskValue / 2), halfRiskAmount, focus, slippage, send)
    #hotkey.TradeHotkeysQuantity(longKeys, shortKeys, tradeQty, focus, slippage, send)
    hotkey.AddHotkey('Ctrl+B', 'Long Buy x Shares', '%sROUTE=MARKET;Share=500;TIF=DAY+;BUY=Load;' % (focus))

    hotkey.AddHotkey('Ctrl+F', 'Long Buy x Shares 100% Risk', 'StopPrice=Price;Price = Ask-Price; Share = %d / Price;ROUTE=SMRTL;Price=Ask+0.03;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:StopPrice ACT:SELL QTY:POS TIF:DAY+' % (riskValue))

    hotkey.AddHotkey('Shift+F', 'Long Buy x Shares 50% risk', 'StopPrice=Price;Price = Ask-Price; Share = %d / Price;ROUTE=SMRTL;Price=Ask+0.03;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:StopPrice ACT:SELL QTY:POS TIF:DAY+' % (riskValue / 2))

    hotkey.AddHotkey('Shift+E', 'Long Buy x Shares At Price', 'DefShare=BP*0.97;Price=Price-StopPrice;SShare=%d/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare; SShare=Share;Share=Price*100; Price=StopPrice; DefShare=Price*100; Price=Share/100; Price=Price+StopPrice; StopPrice=Price; Share=SShare; TogSShare; Price=Price+.03;TIF=DAY+;Route=Stop;StopType=Limit; Buy=Send; Share=DefShare;Price=Share/100; StopPrice=Price; DefShare=400;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue / 2))

    hotkey.AddHotkey('Ctrl+G', 'Short Sell x Shares 100% Risk', 'StopPrice=Price;Price = Price-Bid; Share = %d / Price;ROUTE=SMRTL;Price=Bid-0.03;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:StopPrice ACT:BUY QTY:POS TIF:DAY+' % (riskValue))

    hotkey.AddHotkey('Shift+G', 'Short Sell x Shares 100% Risk', 'StopPrice=Price;Price = Price-Bid; Share = %d / Price;ROUTE=SMRTL;Price=Bid-0.03;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:StopPrice ACT:BUY QTY:POS TIF:DAY+' % (riskValue / 2))

    hotkey.AddHotkey('Shift+S', 'Stop Position', 'StopPrice=Price')
    # exit
    hotkey.CoverShort(coverKeys, sellPercent, focus, clear, 'Cover Short ', send)
    #hotkey.CoverShort(coversKeysStop, sellPercent, focus, clear, 'Cover Short and Adjust Stop', send, True)
    hotkey.SellPosition(sellKeys, sellPercent, focus, clear, 'Exit Long ', send)
    #hotkey.SellPosition(sellKeysStop, sellPercent, focus, clear, 'Exit Long and Adjust Stop ', send, True)
    # Profit targets
    #hotkey.AddHotkey('Ctrl+X', 'Profit Target $.10', 'Route=LIMIT; Share=Pos; Price=ASK+.10; NoRR=N; SELL; TIF=DAY')
    #hotkey.AddHotkey('Ctrl+Y', 'Profit Target $.20', 'Route=LIMIT; Share=Pos; Price=ASK+.20; NoRR=N; SELL; TIF=DAY')
    #hotkey.AddHotkey('Ctrl+Z', 'Profit Target $.30', 'Route=LIMIT; Share=Pos; Price=ASK+.30; NoRR=N; SELL; TIF=DAY')
    # Trailing stopPrice
    hotkey.AddHotkey('Ctrl+J', 'Trail $x.xx', 'CXL ALLSYMB;Share=Pos;ROUTE=STOP;StopType=Trailing;TrailPrice=0.2; TIF=DAY+;SELL=Load;')
    hotkey.AddHotkey('Ctrl+K', 'Trail $0.10', 'CXL ALLSYMB;Share=Pos;ROUTE=STOP;StopType=Trailing;TrailPrice=0.1; TIF=DAY+;SELL=Send;')
    # news
    hotkey.AddHotkey('Ctrl+N', 'News', 'https://www.barchart.com/stocks/quotes/%SYMB%/overview;http://www.benzinga.com/quote/%SYMB%;http://seekingalpha.com/symbol/%SYMB%;https://stocks.jonathongibbs.com/symbol.php?sym=%SYMB%;https://tradingterminal.com/stocks/%SYMB%')
    # premarket
    hotkey.AddHotkey('Shift+N', 'News', 'https://uk.investing.com/equities/pre-market;https://stocktwits.com/stream/trending;')
    hotkey.AddHotkey('Shift+P', 'Profile', 'http://uk.finance.yahoo.com/quote/%SYMB%/profile?p=%SYMB%')
    # Charting
    #hotkey.AddHotkey('Tab','Switch Montage', 'SwitchTWnd')
    hotkey.AddHotkey('NumPad+', 'Chart ZoomIn', 'ZoomIn')
    hotkey.AddHotkey('NumPad-', 'Chart ZoomOut', 'ZoomOut')
    hotkey.AddHotkey('Ctrl+R', 'Draw Rectangle', 'Rectangle')
    hotkey.AddHotkey('Ctrl+T', 'Draw Trendline', 'TrendLine')
    hotkey.AddHotkey('\\', 'Draw HorizontalLine', 'ConfigTrendLine horzline dashline:09ab00:2;HorizontalLine;')
    hotkey.AddHotkey('Ctrl+\\', 'Draw HorizontalLine', 'ConfigTrendLine horzline dashline:ab0000:2;HorizontalLine;')
    hotkey.AddHotkey('Ctrl+D', 'Draw Delete Lines', 'RemoveALLLines')
    hotkey.AddHotkey('Ctrl+NumPad+', 'Chart Show Historic Data', 'GetMoreHistoricalData')
    # Charting time frames
    hotkey.AddHotkey('1', 'Chart 1', 'MinuteChart 1 2d; NumBar 36')
    hotkey.AddHotkey('2', 'Chart 2', 'MinuteChart 2 2d; NumBar 36')
    hotkey.AddHotkey('3', 'Chart 5', 'MinuteChart 5 5d; NumBar 36')
    hotkey.AddHotkey('4', 'Chart 15', 'MinuteChart 15 5d; NumBar 36')
    hotkey.AddHotkey('5', 'Chart 30', 'MinuteChart 30 10d; NumBar 36')
    hotkey.AddHotkey('6', 'Chart 60', 'MinuteChart 60 20d; NumBar 36')
    hotkey.AddHotkey('7', 'Chart D', 'DayChart 1d 60d; Zoomfit')
    hotkey.AddHotkey('8', 'Chart D Large', 'DayChart 1d 120d; Zoomfit')
    # Alert hotkeys
    hotkey.AddHotkey('Ctrl+A', 'Long Alert', 'AlertName=PriceBroke;AlertType=LastPrice;PlaySound=no;AlertOperator=>=;AddAlert;')
    hotkey.AddHotkey('Shift+A', 'Short Alert', 'AlertName=PriceBroke;AlertType=LastPrice;PlaySound=no;AlertOperator=<=;AddAlert;')
    # Adjust stop
    hotkey.AddHotkey('=', 'Long / Short Break Even',focus + clear + 'Route=Stop;Price=AvgCost;StopType=MARKET;STOPPRICE=AvgCost;StopPrice=Round2;Share=Pos;TIF=DAY+;Send=Reverse;')
    hotkey.AddHotkey('Ctrl+S', 'Long Stop Loss Setup', 'Share=Pos;ROUTE=STOP;StopType=Market;StopPrice=Price;TIF=DAY+;SELL=LOAD')
    # Profit Target
    hotkey.AddHotkey('Ctrl+P', 'Profit Target 1.5', 'Route=Limit;Share=Pos*0.5;Price=AvgCost-StopPrice;Price=Price*1.5;Price=Price+AvgCost;Price=Round2;TIF=DAY+;SELL=Send')
    hotkey.AddHotkey('Shift+L', 'Profit Target 2.0', 'Route=Limit;Share=Pos*1;Price=AvgCost-StopPrice;Price=Price*2;Price=Price+AvgCost;Price=Round2;TIF=DAY+;SELL=Send')
    # Profit Target when short
    hotkey.AddHotkey('Shift+U', 'PT 1.5 (Short 100% BP)', 'Route=Limit;Share=Pos*0.5;Price=StopPrice-AvgCost;Price=Price*1.5;Price=AvgCost-Price;Price=Round2;TIF=DAY+;BUY=Send')
    hotkey.AddHotkey('Shift+M', 'PT 2.0 (Short 100% BP)', 'Route=Limit;Share=Pos*1;Price=StopPrice-AvgCost;Price=Price*2;Price=AvgCost-Price;Price=Round2;TIF=DAY+;BUY=Send')

    # Panic
    hotkey.AddHotkey('Ctrl+ESC', 'Cancel All', 'PANIC')
    # Montage
    hotkey.AddHotkey(',', 'Decrease Shares', focus + 'FOCUS Share;FShare=Share-50')
    hotkey.AddHotkey('.', 'Increase Shares', focus + 'FOCUS Share;FShare=Share+50')
    hotkey.AddHotkey('TAB','Focus on Level 2', 'SwitchTWnd;')
    hotkey.AddHotkey('NumPad1','Focus on Level 2 Top', 'FocusWindow montageOne;')
    hotkey.AddHotkey('NumPad2','Focus on Level 2 Mid', 'FocusWindow montageTwo;')
    hotkey.AddHotkey('NumPad3','Focus on Level 2 Bot', 'FocusWindow montageThree;')

    # Save
    hotkey.Save('./Auto_Hotkey.htk')

    print("Hotkey file created. Saved to C:/DAS Trader Pro New/Auto_Hotkey.htk")
