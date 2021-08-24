import requests
import pandas as pd
import arrow
import datetime
from datetime import datetime as d
import os

'''
The ImportSymbols class downloads financial data from a list of symbols from the Yahoo website
'''
class ImportSymbols:
    def __init__(self, destinationPath, dataRange, dataInterval, ticker_list=[]):
        # File paths
        self.destinationPath = destinationPath
        # Variables
        self.dataRange = dataRange
        self.dataInterval = dataInterval
        # Load in the ticker list
        self.tickers = pd.Series(dtype="float64")
        for f in ticker_list:
            self.tickers = self.tickers.append(self.LoadTickerNames(f), ignore_index=True).drop_duplicates()
        self.tickerCount = len(self.tickers)
        # Check directory
        if not os.path.exists(self.destinationPath):
            os.makedirs(self.destinationPath)


    # Print iterations progress
    def PrintProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)


    def LoadTickerNames(self, filepath):
        # Symbol must be first column
        df = pd.read_csv(filepath)
        return df.iloc[:, 0]


    def GetQuoteData(self, symbol):
        # Yahoo prevents access now; use a header to mimic human access
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        # Access data
        res = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=%s' % (symbol, self.dataRange, self.dataInterval),headers=headers)
        data = res.json()
        body = data['chart']['result'][0]
        # Create datetime index
        dt = datetime.datetime
        dt = pd.Series(map(lambda x: arrow.get(x).to('US/Eastern').datetime.replace(tzinfo=None), body['timestamp']), name='Datetime')
        df = pd.DataFrame(body['indicators']['quote'][0], index=dt)
        return df


    def DownloadData(self):
        destinationPath = self.destinationPath + d.today().strftime('%Y-%m-%d') + '/'
        if not os.path.exists(destinationPath):
            os.makedirs(destinationPath)
        # Progress bar
        self.PrintProgressBar(0, self.tickerCount, prefix = 'Downloading:', suffix = 'Complete', length = 50)

        for index, value in self.tickers.items():
            # File destinastion
            fileDestination = destinationPath + value + ".csv"
            # If file exists, do not over write
            if not os.path.exists(fileDestination):
                try:
                    df = self.GetQuoteData(value)
                    # Ensure ordering is consistent
                    df = df[["open","close","high","low","volume"]]
                    df.to_csv(fileDestination, index=True)
                    self.PrintProgressBar(index, self.tickerCount, prefix = 'Downloded: ' + value.ljust(6), suffix = 'Complete', length = 50)
                except Exception as e:
                    # Can fail for numerous reasons including unavailable ticker, server down etc,.
                    self.PrintProgressBar(index, self.tickerCount, prefix = 'Failed   : ' + value.ljust(6), suffix = 'Complete', length = 50)

        self.PrintProgressBar(self.tickerCount, self.tickerCount, prefix = 'Downloading Data Complete', suffix = 'Complete', length = 50)


if __name__ == '__main__':
    # varialbles
    destinationPath = "./downloads/"
    tickerList = ["./files/NASDAQ.csv", "./files/NYSE.csv"]

    # Action
    importData = ImportSymbols(destinationPath, dataRange='60d', dataInterval='5m', ticker_list=tickerList)
    importData.DownloadData()
