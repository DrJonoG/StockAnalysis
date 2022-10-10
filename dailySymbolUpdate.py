
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

import csv
import requests
import pandas as pd

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
apiKey = open('./config/api.conf').readline().rstrip()
listingData = 'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey=' + apiKey

with requests.Session() as s:
    symbols = pd.read_csv(listingData, index_col=0)
    symbols = symbols[((symbols.exchange == 'NYSE') | (symbols.exchange=='NASDAQ'))]

    existingSymbols = pd.read_csv('./config/symbols.csv', index_col=0)
    symbols = symbols[~symbols.index.isin(existingSymbols.index)]

    newSymbols = list()
    symbolList = symbols.index.tolist()

    with open('./config/symbols.csv', 'a') as symbolFile:
        for symbol in symbolList:
            try:
                if len(symbol) > 4: continue
                if '-' in symbol: continue
                print(f"==> Processing {symbol}")
                fundamentalLink = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={apiKey}'
                fD = requests.get(fundamentalLink).json()
                if 'Symbol' in fD:
                    name = fD['Name'].replace(',',' ').replace('\n','').replace('\r','')
                    description = fD['Description'].replace(',',' ').replace('\n','').replace('\r','')
                    newLine = f"{fD['Symbol']},{name},{description},{fD['Exchange']},{fD['Sector'].replace(',',' ')},{fD['Industry'].replace(',',' ')},{fD['MarketCapitalization']},{fD['SharesOutstanding']}\n"
                    symbolFile.write(newLine)
            except Exception:
                print(f"==> Error reading {symbol}")
