import pandas as pd
import numpy as np

class OutputColumns:
    def __init__(self):
        self.df = self.Initialise()

    def Initialise(self):
        columns = [
            'Datetime',
            'EntryDatetime',
            'Exit Datetime',
            'Sym',
            'Position Size',
            'Final size',
            'Entry Price',
            'Original Stop',
            'Adjusted Stop',
            'Profit Target (1)',
            'Profit Target (2)',
            'Profit Target (3)',
            'Profit (1)',
            'Profit (2)',
            'Profit (3)',
            'Exit Price',
            'Exit PnL',
            'PnL',
            'Total Bars',
            'Exit Type'
        ]
        return pd.DataFrame(columns=columns).set_index('Datetime')

    def Get(self):
        return self.df

    def Set(self):
        pass

    def Append(self, data, exit, sym):
        # Data series
        try:
            dataArray = [
                data['entryCandle'].Datetime,
                exit,
                sym,
                round(data['entrySize'],0),
                data['remainingPosition'],
                round(data['entryCandle'].close,2),
                round(data['originalStop'], 2),
                round(data['stopTarget'],2),
                round(data['profitTargets'][0],2),
                round(data['profitTargets'][1],2),
                round(data['profitTargets'][2],2),
                round(data['profits'][0],2),
                round(data['profits'][1],2),
                round(data['profits'][2],2),
                round(data['exitPrice'], 2),
                round(data['exitPNL'],2),
                round(data['profits'][0]+data['profits'][1]+data['profits'][2]+data['exitPNL'], 2),
                data['barCount'],
                data['exitType']
            ]
            self.df.loc[len(self.df)] = dataArray
        except Exception as e:
            print("Error appending to output dataframe.")
            print("Error message: " + e)

    def Save(self):
        pass

class TradeDataFrame():
    def __init__(self):
        self.columns = [
            'entrySize',               # The size of the position
            'remainingPosition',       # The remaioning number of shares
            'totalCost',               # The cost of the position
            'stopTarget',              # The stop target
            'profitTargets',           # The profit target
            'profits',                 # Profit at each target
            'currentTarget',           # The current target reached
            'triggerCandle',           # The candle that touched the ma
            'entryCandle',             # The candle that we enter the trade on
            'barCount',                # Count number of bars in trade
            'exitPrice',
            'exitType',
            'exitPNL',
            'originalStop',
            'sellQty'
        ]
        self.df = self.Initialise()
        self.currentRow = None

    def Initialise(self):
        return pd.DataFrame(columns = self.columns)

    def CreateRow(self):
        self.currentRow = dict.fromkeys(self.columns, 0)
        self.currentRow['profitTargets'] = np.array([0,0,0])
        self.currentRow['profits'] = np.array([0,0,0])

    def Reset(self):
        self.df = self.Initialise()

    def Get(self, column=None):
        if self.currentRow is None:
            self.CreateRow()
        if column:
            return self.currentRow[column]
        else:
            return self.currentRow

    def Set(self, value, column=None, row=None):
        if self.currentRow is None:
            self.CreateRow()
        self.currentRow.update({column: value})

    def Append(self):
        pass


class FigureDictionary():
    def __init__(self):
        self.df = self.Initialise()

    def Initialise(self):
        pass
