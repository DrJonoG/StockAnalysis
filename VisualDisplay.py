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

class VisualDisplay:
    def __init__(self, name, df):
        self.chartName = name
        self.df = df
        self.figure = self.CandleStick

    def CandleStick(self):
        # Create candlestick
        candlestick = go.Candlestick(
            name = self.chartName,
            x = self.df.index,
            open = self.df['open'],
            high = self.df['high'],
            low = self.df['low'],
            close = self.df['close']
        )

        self.figure.add_trace(candlestick, row=1, col=1)

    def AddMarker(self):
        pass

    def AddLine(self):
        pass

    def TextConfig(self, chartTitle="Stock Prices", height=1600, yaxis="Price $ - US Dollars"):
        # Update figure
        self.figure.update_layout(
            title=chartTitle,
            height=height,
            dragmode= 'zoom',
            yaxis=dict(title=yaxis),
            xaxis=dict(type="category", rangeslider_visible=False)
        )

    def Display(self):
        self.figure.show()

    def Save(self):
        print("save")
