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

import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

class Display:
    def __init__(self, name, df):
        self.chartName = name
        self.df = df
        self.CandleStick()

    def CandleStick(self):
        # Create candlestick
        self.figure = go.Figure(dict({
            "data":
                [go.Candlestick(
                    name = self.chartName,
                    x = self.df.index,
                    open = self.df['open'],
                    high = self.df['high'],
                    low = self.df['low'],
                    close = self.df['close']
                )],
            "layout": {
                "title": {
                    "text": self.chartName
                }
            }
        }))


    def AddMarker(self, x, y, symbol, color, size=20):
        self.figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode='markers',
                marker=go.Marker(size=size,
                                 symbol=symbol,
                                 color=color)
                )
            )
        )

    def AddLine(self, column, color="black", width=1):
        self.figure.add_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df[column],
                line=dict(color=color, width=width)
            )
        )

    def TextConfig(self, chartTitle="Stock Prices", height=1600, yaxis="Price $ - US Dollars"):
        # Update figure
        self.figure.update_layout(
            title=chartTitle,
            height=height,
            dragmode= 'zoom',
            yaxis=dict(title=yaxis),
            xaxis=dict(type="category", rangeslider_visible=False)
        )

    def Show(self):
        self.figure.show()

    def Save(self):
        print("save")
