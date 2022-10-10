import os
import datetime
import pandas as pd
from helpers import csvToPandas
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
from core import GetData as getData
from core import GetIndicators as getIndicators

class UpdateData:
    def __init__(self, **argd):
        self.__dict__.update(argd)

        self.data = getData.GetData()
        self.indicators = getIndicators.ComputeIndicators(**argd)
        # Use your own api key here. Read as a single line in a file api.conf
        self.apiKey = open('./config/api.conf').readline().rstrip()

    def Update(self, symbol, destination, dataInterval, month, year):
        """
        https://www.alphavantage.co/documentation/#intraday-extended

        Parameters
        ----------
        symbol : String
            The symbol in which to obtain quote data for
        destination : String
            The location where the files should be saved
        dataInterval : Int
            The time period
        month : String
            The month to obtain data for
        year : String
            The year to obtain data for
        """
        # Location of save path
        saveFile = destination + '/%s.csv' % (symbol)

        dataAddress = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=%s&interval=%s&slice=year%smonth%s&apikey=%s' % (symbol, dataInterval, str(year), str(month), self.apiKey)

        # Get data
        rawData = self.data.GetRaw(dataAddress)

        # Ensure there is a return
        #if rawData is None:
        #    with open(destination + '/error.csv', "a") as file:
        #        file.write(symbol + ', No data found. \n')
        #    return

        # Extract and format data
        newData = self.data.PriceDFSorter(rawData.text)
        # Check if data was retrieved, if not, return.
        if newData is None:
            return

        # Check if existing file
        if os.path.exists(saveFile):
            try:
                # Read existing and convert datetime if exists
                loadDF = csvToPandas(saveFile, asc=False, unicode=True)
                if len(loadDF.index) > 0:
                    # Get latest date from existing data and filter to remove duplicates
                    maxDate = max(loadDF.index)
                    weekNumber = maxDate.week
                    newDate = max(newData.index)
                    newWeek = newDate.week
                    if weekNumber >= newWeek:
                        return
                    else:
                        # Get latest date from existing data and filter to remove duplicates
                        maxDate = max(loadDF.index)
                        newData = newData[newData.index >= maxDate]
            except Exception:
                return

        # If new data available (> 1 to exclude header row)
        if len(newData.index) > 5:
            newData = newData.sort_index()
            # Replace missing date times
            newData = newData.resample(dataInterval).mean()
            # Remove any errors
            newData = newData[[isinstance(newData.index[i], datetime.datetime) for i in range(len(newData))]]
            # Remove weekends
            newData = newData[newData.index.dayofweek < 5]
            # Remove out of hours (except pre and post market)
            newData = newData[(newData.index.time > datetime.time(4, 0)) & (newData.index.time <= datetime.time(20, 00))]
            # Replace nan values previous value if price, or 0 if not
            newData['close'] = newData['close'].fillna(method='ffill')
            newData['open'] = newData['open'].fillna(newData['close'])
            newData['high'] = newData['high'].fillna(newData['close'])
            newData['low'] = newData['low'].fillna(newData['close'])
            newData['volume'] = newData['volume'].fillna(0)
            # Candle direction (bull or bear)
            newData['Candle'] = (newData['close'] - newData['open']).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
            # Determine market hours (0 premarket, 1 open market, 2 postmarket)
            newData.loc[(newData.between_time('04:00:00', '09:30:01').index), 'Market'] = 0
            newData.loc[(newData.between_time('09:30:01', '16:00:00').index), 'Market'] = 1
            newData.loc[(newData.between_time('16:00:01', '20:00:00').index), 'Market'] = 2
            # Calculate VWAP
            if self.vWAP:
                newData = newData.groupby(newData.index.date, group_keys=False).apply(self.indicators.ComputeVWAP)
                newData['vwap'] = newData['vwap'].fillna(method='ffill')
                newData['vwapOpen'] = newData['vwap'].fillna(method='ffill')
                newData.loc[(newData.between_time('16:00:01', '09:29:59').index), 'vwapOpen'] = 0


            # Join if existing file
            if os.path.exists(saveFile):
                sliceAmount = 500
                newData = pd.concat([newData,loadDF[0:sliceAmount]], axis=0)
                # Drop duplicates and sort
                newData = newData[~newData.index.duplicated(keep='first')]
                # Order
                try:
                    newData = newData.sort_index()
                except Exception as e:
                    print(newData)
                    #newData.to_csv(saveFile + '_error.csv', index=True)
                    print(e)

            # Calculate moving_averages
            for period in self.simpleMovingAverage:
                newData[str(period) + "MA"] = round(newData['close'].rolling(period).mean(), self.precision)
            for period in self.expMovingAverage:
                newData[str(period) + "EMA"] = round(newData['close'].ewm(span=period, adjust=False).mean(), self.precision)

            # Calculate RSI
            if self.rsiLength > 0:
                newData["close"] = pd.to_numeric(newData["close"], downcast="float")
                newData["RSI" + str(self.rsiLength)] = self.indicators.ComputeRSI(newData.close.diff())

            # Calculate bollinger bands
            if self.bollingerPeriod > 0:
                newData["BollingerMA"], newData["BollingerUpper"], newData["BollingerLower"] = self.indicators.ComputerBollinger(newData.close, self.bollingerPeriod, self.bollingerStdDev)

            # Replace NaN with 0
            newData = newData.fillna(0)
            # Join files if exist
            if os.path.exists(saveFile):
                newData = pd.concat([newData[sliceAmount:],loadDF], axis=0)
                # Remove any errors
                newData = newData[[isinstance(newData.index[i], datetime.datetime) for i in range(len(newData))]]
            # Sort
            newData = newData.sort_index(ascending=False)
            # Overwrite file
            newData.to_csv(saveFile, index=True)
        return True
