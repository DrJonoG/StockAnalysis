from pathlib import Path
from helpers import PrintProgressBar
from ta.momentum import RSIIndicator
import numpy as np
import pandas as pd
import os

class TickerIndicators(object):
    def __init__(self, **argd):
        self.__dict__.update(argd)

    def ComputeRSI(self, diff):
        # Preserve dimensions off diff values
        upChange = 0 * diff
        downChange = 0 * diff
        # up change is equal to the positive difference, otherwise equal to zero
        upChange[diff > 0] = diff[ diff>0 ]
        # down change is equal to negative deifference, otherwise equal to zero
        downChange[diff < 0] = diff[ diff < 0 ]
        # values are related to exponential decay
        # we set com=rsiLength-1 so we get decay alpha=1/rsiLength
        upChangeAvg   = upChange.ewm(com=self.rsiLength-1 , min_periods=self.rsiLength).mean()
        downChangeAvg = downChange.ewm(com=self.rsiLength-1 , min_periods=self.rsiLength).mean()
        # Calculate RSI value
        return round(100 - (100 / (abs(upChangeAvg/downChangeAvg)+1)), self.precision)

    def ComputerBollinger(self, close, period, stdDev):
        # Calculate moving average and standard deviation on stock close
        movingAverage = close.rolling(period).mean()
        standardDeviation = close.rolling(period).std()
        # Calculate upper and lower bands based on stdDev multiplier
        bollingerUpper = movingAverage + standardDeviation * stdDev
        bollingerLower = movingAverage - standardDeviation * stdDev
        return [movingAverage, bollingerUpper, bollingerLower]

    def ComputeVWAP(self, df):
        volume = df.volume
        close = df.close
        return round(df.assign(vwap=(close * volume).cumsum() / volume.cumsum()),2)

    # Process the master files
    def Calculate(self, source, destination):
        # Check if destination exists
        if not os.path.exists(destination):
            os.makedirs(destination)
        # Get file list
        files = list(Path(source).rglob('*.csv'))
        fileCount = len(files)
        # Progress bar
        PrintProgressBar(0, fileCount, prefix = 'Progress:', suffix = 'Complete', length = 50)
        for index, fileName in enumerate(files):
            tickerDF = pd.read_csv(fileName)
            # File name
            fileName = Path(fileName).name
            PrintProgressBar(index, fileCount, prefix = 'Progress: ' + str(fileName).ljust(10), suffix = 'Complete', length = 50)
            # Convert to datetime
            tickerDF['Datetime']= pd.to_datetime(tickerDF['Datetime'])
            # Replace nan values previous value if price, or 0 if not
            tickerDF['close'] = tickerDF['close'].fillna(method='ffill')
            tickerDF['open'] = tickerDF['open'].fillna(tickerDF['close'])
            tickerDF['high'] = tickerDF['high'].fillna(tickerDF['close'])
            tickerDF['low'] = tickerDF['low'].fillna(tickerDF['close'])
            # Candle direction (bull or bear)
            tickerDF['Candle'] = (tickerDF['close'] - tickerDF['open']).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
            # Calculate moving_averages
            for period in self.simpleMovingAverage:
                tickerDF[str(period) + "MA"] = round(tickerDF['close'].rolling(period).mean(), self.precision)
            for period in self.expMovingAverage:
                tickerDF[str(period) + "EMA"] = round(tickerDF['close'].ewm(span=period, adjust=False).mean(), self.precision)
            # Calculate RSI
            if self.rsiLength > 0:
                tickerDF["RSI" + str(self.rsiLength)] = self.ComputeRSI(tickerDF.close.diff(1))
            # Calculate bollinger bands
            if self.bollingerPeriod > 0:
                tickerDF["BollingerMA"], tickerDF["BollingerUpper"], tickerDF["BollingerLower"] = self.ComputerBollinger(tickerDF.close, self.bollingerPeriod, self.bollingerStdDev)
            # Calculate VWAP
            if self.vWAP:
                tickerDF = tickerDF.groupby(tickerDF['Datetime'].dt.date, group_keys=False).apply(self.ComputeVWAP)
            # Replace NaN with 0
            tickerDF = tickerDF.fillna(0)
            # Save
            tickerDF.to_csv(destination + fileName, index=True)

        # Finished
        PrintProgressBar(fileCount, fileCount, prefix = 'Progress: ' + str(fileName).ljust(10), suffix = 'Complete', length = 50)

if __name__ == '__main__':
    # varialbles
    sourcePath = "./downloads/"
    destinationPath = "./downloads/processed/"
    # Define indicators
    indicators = {
        'expMovingAverage': [3, 5, 10, 20, 50, 100],
        'simpleMovingAverage': [],
        'rsiLength': 14,
        'bollingerPeriod': 20,
        'bollingerStdDev': 1.5,
        'vWAP': True,
        'precision': 2
    }

    # Action
    tickerIndicators = TickerIndicators(**indicators)
    tickerIndicators.Calculate(sourcePath, destinationPath)
