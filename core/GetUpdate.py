
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
from core import GetData
from core import GetIndicators

class UpdateData:
    def __init__(self, **argd):
        self.__dict__.update(argd)

        data = GetData()
        indicators = ComputeIndicators()

    def Update(symbol, destination, dataInterval, month, year, merge=True, dateFilter=True):
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
            The month to obtain data for, '*' for all data.
        year : String
            The year to obtain data for, '*' for all data.
        merge : Bool
            Whether to merge the files if * is used, or save them individually
        """
        # Location of save path
        saveFile = destination + '/%s.csv' % (symbol)


        monthRequest = [month]
        yearRequest = [year]

        # Iterate through the yars and months to get data
        for y in yearRequest:
            for m in monthRequest:
                dataAddress = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=%s&interval=%s&slice=year%smonth%s&apikey=%s' % (symbol, dataInterval, str(y), str(m), self.apiKey)
                # Get data
                rawData = data.GetRaw(dataAddress)
                # Ensure there is a return
                if rawData is None:
                    with open(destination + '/error.csv', "a") as file:
                        file.write(symbol + ', No data found. \n')
                    continue
                # Extract and format data
                newData = data.PriceDFSorter(rawData.text)
                # Check if data was retrieved, if not, return.
                if newData is None:
                    continue
                # Remove weekends
                newData = newData[newData.dayofweek < 5]
                # Remove out of hours (except pre and post market)
                newData = newData[(newData.time > datetime.time(4, 0)) & (newData.time <= datetime.time(20, 00))]
                # Get a list of holidays between the start and end
                USHolidays =  calendar().holidays(start=start, end=end)
                # Remove public holidays
                m = newData.isin(USHolidays) # TODO check this
                newData = newData[~m].copy()
                # Replace nan values previous value if price, or 0 if not
                newData['close'] = newData['close'].fillna(method='ffill')
                newData['open'] = newData['open'].fillna(newData['close'])
                newData['high'] = newData['high'].fillna(newData['close'])
                newData['low'] = newData['low'].fillna(newData['close'])

                # Read existing and convert datetime
                loadDF = csvToPandas(saveFile, asc=False, unicode=True)
                if len(loadDF) == 0:
                    continue
                # Get latest date from existing data and filter to remove duplicates
                maxDate = max(loadDF.index)
                newData = newData[newData.index > maxDate]
                # If new data available
                if len(newData) > 0:
                    # Candle direction (bull or bear)
                    newData['Candle'] = (newData['close'] - newData['open']).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

                    # Calculate VWAP
                    if self.vWAP:
                        newData = newData.groupby(newData.index.date, group_keys=False).apply(self.ComputeVWAP)
                        newData['vwap'] = newData['vwap'].fillna(method='ffill')
                        newData.loc[(newData.between_time('16:00:01', '09:29:59').index), 'vwap'] = 0

                    # Join
                    newData = pd.concat([newData,loadDF], axis=0)

                    # Calculate moving_averages
                    for period in self.simpleMovingAverage:
                        newData[str(period) + "MA"] = round(newData['close'].rolling(period).mean(), self.precision)
                    for period in self.expMovingAverage:
                        newData[str(period) + "EMA"] = round(newData['close'].ewm(span=period, adjust=False).mean(), self.precision)

                    # Calculate RSI
                    if self.rsiLength > 0:
                        newData["RSI" + str(self.rsiLength)] = indicators.ComputeRSI(newData.close.diff(1))

                    # Calculate bollinger bands
                    if self.bollingerPeriod > 0:
                        newData["BollingerMA"], newData["BollingerUpper"], newData["BollingerLower"] = indicators.ComputerBollinger(newData.close, self.bollingerPeriod, self.bollingerStdDev)

                    # Replace NaN with 0
                    newData = newData.fillna(0)

                    # Drop duplicates and sort
                    newData = newData[~newData.index.duplicated(keep='first')]
                    newData = newData.sort_index(ascending=False)
                    # Overwrite file
                    newData.to_csv(saveFile, index=True)


        return True
