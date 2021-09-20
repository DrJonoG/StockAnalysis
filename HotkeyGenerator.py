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

# Important # NOTE:
#
# I do not take any responsbility for the use of the hotkeys, all generated hotkeys should be fully tested prior to use
# in a simulated environment
#


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

    def CoverShort(self, keys, percent, focus, clear, name, send, stop=False):
        if len(keys) != len(percent):
            return "Error: Length must be the same."
        adjustStop = ''
        if stop:
            adjustStop = 'ROUTE=STOP;StopType=Market;StopPrice=AvgCost;Share=Pos-share;TIF=GTC;BUY=SEND'
        for i in range(0, len(percent)):
            command = focus + clear + 'ROUTE=LIMIT;Price=ASK+0.01;Price=Round2;Share=Pos*' + str(percent[i]) + ';TIF=DAY+;BUY=' + send + ';'
            self.AddHotkey(keys[i], name + str(percent[i]*100) + '%.', command)

    def SellPosition(self, keys, percent, focus, clear, name, send, stop=False):
        if len(keys) != len(percent):
            return "Error: Length must be the same."
        adjustStop = ''
        if stop:
            adjustStop = 'ROUTE=STOP;StopType=Market;StopPrice=AvgCost;Share=Pos-share;TIF=DAY;SELL=SEND'
        for i in range(0, len(percent)):
            command = focus + clear + 'ROUTE=LIMIT;Price=BID-0.01;Price=Round2;Share=Pos*' + str(percent[i]) + ';TIF=DAY;SELL=' + send + ';' + adjustStop
            self.AddHotkey(keys[i], name + str(percent[i]*100) + '%.', command)

    def ShortLongHotkeys(self, longKeys, shortKeys, tradeQty, focus, send):
        for i in range(0, 10):
            if len(longKeys) >= i:
                buyCommand = focus + 'ROUTE=SMRTL;Price=Ask+0.01;Share=%s;Price=%s;StopPrice=Ask-Price;Price=Ask+.01;TIF=DAY+;BUY=%s;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:StopPrice ACT:SELL QTY:POS TIF:DAY+' % (str(tradeQty[i]), str(round(riskValue/tradeQty[i], 2)), send)
                self.AddHotkey(longKeys[i], 'Long %s' % str(tradeQty[i]), buyCommand)
            if len(shortKeys) >= i:
                sellCommand = focus + 'ROUTE=SMRTL;Price=Ask+0.01;Share=%s;Price=%s;StopPrice=Ask+Price;Price=Ask-.01;TIF=DAY+;SELL=%s;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:StopPrice ACT:BUY QTY:POS TIF:DAY+' % (str(tradeQty[i]), str(round(riskValue/tradeQty[i], 2)), send)
                self.AddHotkey(shortKeys[i], 'Short %s' % str(tradeQty[i]), sellCommand)

    def Save(self, path):
        self.configDF = self.configDF.sort_values(by='Name', ascending=True, key=lambda col: col.str.lower())
        # Path to das trader directory, do not overwrite original hotkey file.
        with open(path, 'w') as f:
            for index, row in self.configDF.iterrows():
                f.write(str(row['Key']) + ':' + row['Name'] + ':' + row['Command'] + '\n')


if __name__ == '__main__':
    riskValue = 200
    focus = 'FocusWindow Level2;'
    clear = 'CXL ALLSYMB;'
    send = 'Send'
    # long and short hotkeys
    longKeys = [1,2,3,4,5,6,7,8,9,0]
    shortKeys = ['F1', 'F2','F3', 'F4','F5', 'F6','F7', 'F8','F9', 'F10']
    tradeQty = [100, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 5000]
    # Sell and cover positions
    coverKeys = ['Delete','End', 'PageDown']
    sellKeys = ['Insert','Home','PageUp']
    sellKeysStop = ['Ctrl+Insert','Ctrl+Home','Ctrl+PageUp']
    coversKeysStop = ['Ctrl+Delete','Ctrl+End', 'Ctrl+PageDown']
    sellPercent = [.25, .5, 1]
    # Initialise hotkeys config df
    hotkey = HotKeys()
    # trade
    hotkey.ShortLongHotkeys(longKeys, shortKeys, tradeQty, focus, send)
    hotkey.AddHotkey('Ctrl+B', 'Long Buy x Shares', focus + 'ROUTE=SMRTL;Price=Ask+0.01;Share=1000;TIF=DAY+;BUY=Load;')
    # exit
    hotkey.CoverShort(coverKeys, sellPercent, focus, clear, 'Cover Short ', send)
    hotkey.CoverShort(coversKeysStop, sellPercent, focus, clear, 'Cover Short and Adjust Stop', send, True)
    hotkey.SellPosition(sellKeys, sellPercent, focus, clear, 'Exit Long ', send)
    hotkey.SellPosition(sellKeysStop, sellPercent, focus, clear, 'Exit Long and Adjust Stop ', send, True)
    # news
    hotkey.AddHotkey('Y', 'Yahoo News', 'https://uk.finance.yahoo.com/quote/%SYMB%/news?p=%SYMB%')
    # Charting
    hotkey.AddHotkey('NumPad+', 'Chart ZoomIn', 'ZoomIn')
    hotkey.AddHotkey('NumPad-', 'Chart ZoomOut', 'ZoomOut')
    hotkey.AddHotkey('Ctrl+R', 'Draw Rectangle', 'Rectangle')
    hotkey.AddHotkey('Ctrl+T', 'Draw Trendline', 'TrendLine')
    hotkey.AddHotkey('/', 'Draw HorizontalLine', 'HorizontalLine')
    hotkey.AddHotkey('Ctrl+D', 'Draw Delete Lines', 'RemoveALLLines')
    hotkey.AddHotkey('Ctrl+NumPad+', 'Chart Show Historic Data', 'GetMoreHistoricalData')
    # Alert hotkeys
    hotkey.AddHotkey('Ctrl+A', 'Long Alert', 'AlertName=PriceBroke;AlertType=LastPrice;PlaySound=no;AlertOperator=>=;AddAlert;')
    hotkey.AddHotkey('Shift+A', 'Short Alert', 'AlertName=PriceBroke;AlertType=LastPrice;PlaySound=no;AlertOperator=<=;AddAlert;')
    # Adjust stop
    hotkey.AddHotkey('=', 'Long / Short Break Even',focus + clear + 'Route=Stop;Price=AvgCost;StopType=MARKET;STOPPRICE=AvgCost;StopPrice=Round2;Share=Pos;TIF=DAY+;Send=Reverse;')
    hotkey.AddHotkey('Ctrl+S', 'Long Stop Loss Setup', 'Share=Pos;ROUTE=STOP;StopType=Market;StopPrice=Price;TIF=DAY+;SELL=LOAD')
    # Panic
    hotkey.AddHotkey('Ctrl+ESC', 'Cancel All', 'FocusWindow Level2;CXL ALLSYMB')
    # Montage
    hotkey.AddHotkey(',', 'Decrease Shares', focus + 'FOCUS Share;FShare=Share-50')
    hotkey.AddHotkey('.', 'Increase Shares', focus + 'FOCUS Share;FShare=Share+50')
    # Save
    hotkey.Save('C:/DAS Trader Pro New/Auto_Hotkey.htk')
