
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
import csv
import re
import time
import requests
import pandas as pd
from datetime import datetime

def downloadSymbolData(existingPath = './config/symbols.csv'):
    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    apiKey = open('./config/api.conf').readline().rstrip()
    listingData = 'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey=' + apiKey

    with requests.Session() as s:
        symbols = pd.read_csv(listingData, index_col=0)
        symbols = symbols[((symbols.exchange == 'NYSE') | (symbols.exchange=='NASDAQ'))]

        if os.path.exists(existingPath):
            # Get file's Last modification time stamp only in terms of seconds since epoch
            modTimesinceEpoc = os.path.getmtime(existingPath)
            # Convert seconds since epoch to readable timestamp
            modificationTime = time.strftime('%Y-%m-%d', time.localtime(modTimesinceEpoc))
            currentDate = datetime.now().strftime("%Y-%m-%d")
            # Check if file has already been modified today
            if currentDate == modificationTime:
                awaitingResponse = True
                while(awaitingResponse):
                    response = input("==> The symbol file has already been updated today, are you sure you wish to update again? (Y/N): ")
                    if response.lower() == "y":
                        awaitingResponse = False
                    if response.lower() == "n":
                        return False

            existingSymbols = pd.read_csv(existingPath, index_col=0)
            symbols = symbols[~symbols.index.isin(existingSymbols.index)]

        # Convert to list
        symbolList = symbols.index.tolist()
        numSymbols = len(symbolList)

        with open('./config/symbols.csv', 'a') as symbolFile:
            for count, symbol in enumerate(symbolList):
                # Check if symbol is valid
                if not isinstance(symbol, str) or len(symbol) > 4 or '-' in symbol:
                    continue
                # Output progress
                now = datetime.now().strftime("%H:%M:%S")
                print(now + f" ==> Processing symbol {count} of {numSymbols}.", end="\r")
                # Store errors
                errorList = []
                try:
                    # Obtain fundamental
                    fundamentalLink = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={apiKey}'
                    fD = requests.get(fundamentalLink).json()
                    if 'Symbol' in fD:
                        name = fD['Name'].replace(',',' ').replace('\n','').replace('\r','')
                        description = fD['Description'].replace(',',' ').replace('\n','').replace('\r','')
                        # Remove characters
                        name = re.sub(r'[^a-zA-Z0-9\._-\s+]', '', name)
                        description = re.sub(r'[^a-zA-Z0-9\._-\s+]', '', description)
                        exchange = re.sub(r'[^a-zA-Z0-9\._-\s+]', '', fD['Exchange'])
                        sector = re.sub(r'[^a-zA-Z0-9\._-\s+]', '', fD['Sector'].replace(',',' '))
                        industry = re.sub(r'[^a-zA-Z0-9\._-\s+]', '', fD['Industry'].replace(',',' '))
                        symbol = re.sub(r'[^a-zA-Z0-9\._-\s+]', '', fD['Symbol'])
                        # Generate line
                        newLine = f"{symbol},{name},{description},{exchange},{sector},{industry},{fD['MarketCapitalization']},{fD['SharesOutstanding']}\n"
                        symbolFile.write(newLine)
                except Exception:
                    errorList.append(symbol)

        now = datetime.now().strftime("%H:%M:%S")
        print(now + f" ==> Symbol list and fundamental data download complete.", end="\n")

        if len(errorList) > 0:
            print(now + f" ==> Errornous symbols: \n {str(errorList)}", end="\r")

        return True
