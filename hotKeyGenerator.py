
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


    def Save(self, path):
        self.configDF = self.configDF.sort_values(by='Name', ascending=True, key=lambda col: col.str.lower())
        # Path to das trader directory, do not overwrite original hotkey file.
        with open(path, 'w') as f:
            for index, row in self.configDF.iterrows():
                f.write(str(row['Key']) + ':' + row['Name'] + ':' + row['Command'] + '\n')


if __name__ == '__main__':
    # Adjust your risk value here to automatically increase the position sizes
    #accountSize = input("==> Please enter account size: ")
    accountSize = 5000#int(accountSize)

    #riskPercent = input("==> Please enter risk percentage (1-100): ")
    riskPercent = 0.01#float(riskPercent) / 100

    riskValue = accountSize * riskPercent
    focus = 'FocusWindow Level2;' #'FocusWindow Level2;'
    clear = 'CXL ALLSYMB;'
    send = 'Send'
    slippage = '0.02'

    # Initialise hotkeys config df
    hotkey = HotKeys()

    # Charting
    hotkey.AddHotkey('Tab','Switch Montage', 'SwitchTWnd')
    hotkey.AddHotkey('NumPad+', 'Chart ZoomIn', 'ZoomIn')
    hotkey.AddHotkey('NumPad-', 'Chart ZoomOut', 'ZoomOut')
    hotkey.AddHotkey('Ctrl+R', 'Draw Rectangle', 'ConfigTrendLine rectangle dashline:EDEFFF:0:EDEFFF:40:1;Rectangle')
    hotkey.AddHotkey('Ctrl+T', 'Draw Trendline', 'TrendLine')
    hotkey.AddHotkey('\\', 'Draw HorizontalLine', 'ConfigTrendLine horzline dashline:09ab00:2;HorizontalLine;')
    hotkey.AddHotkey('Ctrl+\\', 'Draw HorizontalLine', 'ConfigTrendLine horzline dashline:ab0000:2;HorizontalLine;')
    hotkey.AddHotkey('Ctrl+D', 'Draw Delete Lines', 'RemoveALLLines')
    hotkey.AddHotkey('Ctrl+NumPad+', 'Chart Show Historic Data', 'GetMoreHistoricalData')

    # Charting time frames
    hotkey.AddHotkey('1', 'Chart 1', 'MinuteChart 1 2d; LoadSetting chartOneMin.cst;')
    hotkey.AddHotkey('2', 'Chart 2', 'MinuteChart 2 2d; LoadSetting chartTwoMin.cst;')
    hotkey.AddHotkey('3', 'Chart 5', 'MinuteChart 5 5d; LoadSetting chartFiveMin.cst;')
    hotkey.AddHotkey('4', 'Chart 15', 'MinuteChart 15 5d; LoadSetting chartFifteenMin.cst;')
    hotkey.AddHotkey('5', 'Chart 30', 'MinuteChart 30 20d; LoadSetting chartThirtyMin.cst;')
    hotkey.AddHotkey('6', 'Chart 60', 'MinuteChart 60 30d; LoadSetting chartSixtyMin.cst;')
    hotkey.AddHotkey('7', 'Chart D', 'DayChart 1d 52w; LoadSetting chartOneDay.cst; Zoomfit')
    hotkey.AddHotkey('8', 'Chart D Large', 'DayChart 1d 52w; LoadSetting chartOneDay.cst;')

    # General
    hotkey.AddHotkey('Shift+S', 'Set Stop Position', 'FocusWindow Level2;StopPrice=Price;')
    hotkey.AddHotkey('Ctrl+ESC', 'Cancel All', 'PANIC')
    hotkey.AddHotkey('Alt+ESC', 'Cancel Sym', 'CXL ALLSYMB;')

    # Shorts - shorting on a downtrend on the bid

    hotkey.AddHotkey('Ctrl+S', 'Short @ 100% Risk', 'StopPrice=Price+0;DefShare=BP*0.99;Price=Price-Bid+0.00;SShare=%s/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare;TogSShare;ROUTE=SMRTL;Price=Bid-%s;TIF=DAY+;SELL=Send;DefShare=200;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice+%s ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue, slippage, slippage))
    hotkey.AddHotkey('Shift+G', 'Short @ 50% Risk', 'StopPrice=Price+0;DefShare=BP*0.99;Price=Price-Bid+0.00;SShare=%s/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare;TogSShare;ROUTE=SMRTL;Price=Bid-%s;TIF=DAY+;SELL=Send;DefShare=200;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice+%s ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue / 2, slippage, slippage))
    hotkey.AddHotkey('Shift+I', 'Short @ 25% Risk', 'StopPrice=Price+0;DefShare=BP*0.99;Price=Price-Bid+0.00;SShare=%s/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare;TogSShare;ROUTE=SMRTL;Price=Bid-%s;TIF=DAY+;SELL=Send;DefShare=200;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice+%s ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue / 4, slippage, slippage))
    hotkey.AddHotkey('Ctrl+I', 'Short @ 10% Risk', 'StopPrice=Price+0;DefShare=BP*0.99;Price=Price-Bid+0.00;SShare=%s/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare;TogSShare;ROUTE=SMRTL;Price=Bid-%s;TIF=DAY+;SELL=Send;DefShare=200;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice+%s ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue / 10, slippage, slippage))

    # Longs - buying in an uptrending market on the ask

    hotkey.AddHotkey('Ctrl+F', 'Long @ 100% Risk', 'StopPrice=Price-0;DefShare=BP*0.99;Price=Ask-Price+0.00;SShare=%s/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare;TogSShare;ROUTE=SMRTL;Price= Ask+%s;TIF=DAY+;BUY=Send;DefShare=200;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0.%s ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue, slippage, slippage))
    hotkey.AddHotkey('Shift+F', 'Long @ 50% risk', 'StopPrice=Price-0;DefShare=BP*0.99;Price=Ask-Price+0.00;SShare=%s/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare;TogSShare;ROUTE=SMRTL;Price= Ask+%s;TIF=DAY+;BUY=Send;DefShare=200;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0.%s ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue / 2, slippage, slippage))
    hotkey.AddHotkey('Shift+L', 'Long @ 25% risk', 'StopPrice=Price-0;DefShare=BP*0.99;Price=Ask-Price+0.00;SShare=%s/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare;TogSShare;ROUTE=SMRTL;Price= Ask+%s;TIF=DAY+;BUY=Send;DefShare=200;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0.%s ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue / 4, slippage, slippage))
    hotkey.AddHotkey('Ctrl+L', 'Long @ 10% risk', 'StopPrice=Price-0;DefShare=BP*0.99;Price=Ask-Price+0.00;SShare=%s/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare;TogSShare;ROUTE=SMRTL;Price= Ask+%s;TIF=DAY+;BUY=Send;DefShare=200;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0.%s ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue / 10, slippage, slippage))

    # Shorts cover
    hotkey.AddHotkey('Delete', 'Cover 25% @ Bid', '%sROUTE=LIMIT;Price=BID;Share=Pos*0.25;TIF=DAY;BUY=Send;' % (focus))
    hotkey.AddHotkey('End', 'Cover 50% @ Bid', '%sROUTE=LIMIT;Price=BID;Share=Pos*0.5;TIF=DAY;BUY=Send;' % (focus))
    hotkey.AddHotkey('PageDown', 'Cover 100% @ Ask', '%sROUTE=LIMIT;Price=ASK;Share=Pos;TIF=DAY;BUY=Send;CXL ALLSYMB;' % (focus))

    # Longs sell
    hotkey.AddHotkey('Insert', 'Sell 25% @ Ask', '%sROUTE=LIMIT;Price=ASK;Share=Pos*0.25;TIF=DAY;SELL=Send;' % (focus))
    hotkey.AddHotkey('Home', 'Sell 50% @ Ask', '%sROUTE=LIMIT;Price=ASK;Share=Pos*0.5;TIF=DAY;SELL=Send;' % (focus))
    hotkey.AddHotkey('PageUp', 'Sell 100% @ Bid', '%sROUTE=LIMIT;Price=BID;Share=Pos;TIF=DAY;SELL=Send;CXL ALLSYMB;' % (focus))


    # TODO: These all require implementation


    # Adjust stop
    hotkey.AddHotkey('Ctrl+NumPad-', 'Stop B/E','FocusWindow Level2;CXL ALLSYMB;Route=Stop;StopPrice=AvgCost;StopType=MARKET;STOPPRICE=StopPrice;Share=Pos;TIF=DAY+;Send=Reverse;')
    hotkey.AddHotkey('Ctrl+NumPad/', 'Stop (1R)','FocusWindow Level2;CXL ALLSYMB;Route=Stop;Price=%d/Pos;StopPrice=AvgCost-Price;StopType=MARKET;STOPPRICE=StopPrice;Share=Pos;TIF=DAY+;Send=Reverse;' % (riskValue))
    hotkey.AddHotkey('Ctrl+NumPad.', 'Stop (0.5R)','FocusWindow Level2;CXL ALLSYMB;Route=Stop;Price=%d/Pos;StopPrice=AvgCost-Price;StopType=MARKET;STOPPRICE=StopPrice;Share=Pos;TIF=DAY+;Send=Reverse;' %((riskValue / 2)))
    hotkey.AddHotkey('Ctrl+Y', 'Stop Adjust', 'Share=Pos;ROUTE=STOP;StopType=Market;StopPrice=Price;TIF=DAY+;SELL=LOAD') # Send = Reverse?
    hotkey.AddHotkey('Ctrl+J', 'Trail $x.xx', 'CXL ALLSYMB;Share=Pos;ROUTE=STOP;StopType=Trailing;TrailPrice=0.2; TIF=DAY+;SELL=Load;') # Send = Reverse? And trail price = $R / Shares * .5 ?


    # Short PT
    hotkey.AddHotkey('Alt+NumPad1', 'Short PT 1.5', 'FocusWindow Level2;Route=Limit;Share=Pos*0.50;Price=StopPrice-AvgCost;Price=Price*1.5;Price=AvgCost-Price;TIF=DAY+;BUY=Send')
    hotkey.AddHotkey('Alt+NumPad2', 'Short PT 2.0', 'FocusWindow Level2;Route=Limit;Share=Pos*0.35;Price=StopPrice-AvgCost;Price=Price*2;Price=AvgCost-Price;TIF=DAY+;BUY=Send')
    hotkey.AddHotkey('Alt+NumPad3', 'Short PT 3.0', 'FocusWindow Level2;Route=Limit;Share=Pos*0.25;Price=StopPrice-AvgCost;Price=Price*3;Price=AvgCost-Price;TIF=DAY+;BUY=Send')

    # Long PT
    hotkey.AddHotkey('Ctrl+NumPad1', 'Long PT 1.5', 'FocusWindow Level2;Route=Limit;Share=Pos*0.50;Price=AvgCost-StopPrice;Price=Price*1.5;Price=Price+AvgCost;TIF=DAY+;SELL=Send')
    hotkey.AddHotkey('Ctrl+NumPad2', 'Long PT 2.0', 'FocusWindow Level2;Route=Limit;Share=Pos*0.35;Price=AvgCost-StopPrice;Price=Price*2;Price=Price+AvgCost;TIF=DAY+;SELL=Send')
    hotkey.AddHotkey('Ctrl+NumPad3', 'Long PT 3.0', 'FocusWindow Level2;Route=Limit;Share=Pos*0.25;Price=AvgCost-StopPrice;Price=Price*3;Price=Price+AvgCost;TIF=DAY+;SELL=Send')

    # Short at $x
    hotkey.AddHotkey('Alt+R', 'Short @ $x.xx (1R)', 'DefShare=BP*0.97;Price=StopPrice-Price;SShare=%s/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare; SShare=Share;Share=Price*100; Price=StopPrice; DefShare=Price*100; Price=Share/100; Price=StopPrice-Price; StopPrice=Price; Share=SShare; TogSShare; Price=Price-%s;TIF=DAY+;Route=Stop;StopType=Limit; Sell=Send; Share=DefShare;Price=Share/100; StopPrice=Price; DefShare=400;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue, slippage))

    # Long at $x
    hotkey.AddHotkey('Shift+E', 'Long @ $x.xx (1R)', 'DefShare=BP*0.97;Price=Price-StopPrice;SShare=%s/Price;Share=DefShare-SShare;DefShare=DefShare+SShare;SShare=Share;Sshare=DefShare-SShare;Share=0.5*SShare; SShare=Share;Share=Price*100; Price=StopPrice; DefShare=Price*100; Price=Share/100; Price=Price+StopPrice; StopPrice=Price; Share=SShare; TogSShare; Price=Price+%s;TIF=DAY+;Route=Stop;StopType=Limit; Buy=Send; Share=DefShare;Price=Share/100; StopPrice=Price; DefShare=400;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;' % (riskValue, slippage))

    # Longs - buying in an uptrending market on the ask # Testing
    #'hotkey.AddHotkey('Ctrl+-', 'BHOD (1R)', '%sPrice=HI-StopPrice;DefShare = %d/Price; ROUTE=STOP;StopType=Limit;Price=HI+0.05;StopPrice=HI;Share=DefShare;TIF=DAY+;BUY=Send;StopPrice=%d/DefShare;StopPrice=HI-StopPrice;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:StopPrice ACT:SELL QTY:POS TIF:DAY+;' % (focus, riskValue, riskValue))

    # Shorts add



    # Short BLOD
    #hotkey.AddHotkey('Ctrl+M', 'BLOD @ 50% Risk', '%sStopPrice=Price;TrailPrice=StopPrice-0.01;Price=StopPrice-LOW;DefShare = %d/Price; ROUTE=STOP;StopType=Limit;Price=LOW-0.02;StopPrice=LOW;Share=DefShare;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:TrailPrice ACT:BUY QTY:POS TIF:DAY+;' % (focus, (riskValue/ 2)))
    #hotkey.AddHotkey('Shift+M', 'BLOD @ 100% Risk', '%sStopPrice=Price;TrailPrice=StopPrice-0.01;Price=StopPrice-LOW;DefShare = %d/Price; ROUTE=STOP;StopType=Limit;Price=LOW-0.02;StopPrice=LOW;Share=DefShare;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:TrailPrice ACT:BUY QTY:POS TIF:DAY+;' % (focus, riskValue))

    # Short at $x
    #hotkey.AddHotkey('Alt+R', 'Short @ $x.xx (1R)', '%sTrailPrice=StopPrice;StopPrice=StopPrice-Price;DefShare = %d/StopPrice; ROUTE=STOP;StopType=Limit;StopPrice=Price;Price=Price-0.02;Share=DefShare;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:TrailPrice ACT:BUY QTY:POS TIF:DAY+;' % (focus, riskValue))




    ###
    ## LONG
    ###



    # Longs add



    # Long BHOD
    #hotkey.AddHotkey('-', 'BHOD (0.5R)', '%sStopPrice=Price;TrailPrice=StopPrice+0.01;Price=HI-StopPrice;DefShare = %d/Price; ROUTE=STOP;StopType=Limit;Price=HI+0.02;StopPrice=HI;Share=DefShare;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:TrailPrice ACT:SELL QTY:POS TIF:DAY+;' % (focus, (riskValue/ 2)))
    #hotkey.AddHotkey('Ctrl+-', 'BHOD (1R)', '%sStopPrice=Price;TrailPrice=StopPrice+0.01;Price=HI-StopPrice;DefShare = %d/Price; ROUTE=STOP;StopType=Limit;Price=HI+0.02;StopPrice=HI;Share=DefShare;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:TrailPrice ACT:SELL QTY:POS TIF:DAY+;' % (focus, riskValue))
    #TrailPrice=StopPrice;Price=HI-StopPrice;DefShare = 100/Price; ROUTE=STOP;StopType=Market;Price=HI+0.02;StopPrice=HI;Share=DefShare;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET STOPPRICE:TrailPrice ACT:SELL QTY:POS TIF:DAY+;





    # Super scalping

    hotkey.AddHotkey('Ctrl+1', 'Long @ $0.05 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Ask-0.05;Price=Ask+0.01;Share=%s;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.05)))
    hotkey.AddHotkey('Ctrl+2', 'Long @ $0.10 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Ask-0.10;Price=Ask+0.01;Share=%s;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.10)))
    hotkey.AddHotkey('Ctrl+3', 'Long @ $0.15 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Ask-0.15;Price=Ask+0.01;Share=%s;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.15)))
    hotkey.AddHotkey('Ctrl+4', 'Long @ $0.20 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Ask-0.20;Price=Ask+0.01;Share=%s;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.20)))
    hotkey.AddHotkey('Ctrl+5', 'Long @ $0.30 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Ask-0.30;Price=Ask+0.01;Share=%s;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.30)))
    hotkey.AddHotkey('Ctrl+6', 'Long @ $0.50 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Ask-0.50;Price=Ask+0.01;Share=%s;TIF=DAY+;BUY=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:SELL STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.50)))

    hotkey.AddHotkey('Alt+1', 'Short @ $0.05 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Bid+0.05;Price=Bid-0.01;Share=%s;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.05)))
    hotkey.AddHotkey('Alt+2', 'Short @ $0.10 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Bid+0.10;Price=Bid-0.01;Share=%s;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.10)))
    hotkey.AddHotkey('Alt+3', 'Short @ $0.15 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Bid+0.15;Price=Bid-0.01;Share=%s;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.15)))
    hotkey.AddHotkey('Alt+4', 'Short @ $0.20 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Bid+0.20;Price=Bid-0.01;Share=%s;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.20)))
    hotkey.AddHotkey('Alt+5', 'Short @ $0.30 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Bid+0.30;Price=Bid-0.01;Share=%s;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.30)))
    hotkey.AddHotkey('Alt+6', 'Short @ $0.50 Risk', "FocusWindow Level2;ROUTE=LIMIT;StopPrice=Bid+0.50;Price=Bid-0.01;Share=%s;TIF=DAY+;SELL=Send;TriggerOrder=RT:STOP STOPTYPE:MARKET PX:StopPrice-0 ACT:BUY STOPPRICE:StopPrice QTY:Pos TIF:DAY+;" % (int(riskValue / 0.50)))



    # Save
    #C:/DAS Trader Pro
    hotkey.Save('C:/DAS Trader Pro/Auto_Hotkey.htk')

    print("==> Hotkey file created. Saved to C:/DAS Trader Pro/Auto_Hotkey.htk")
