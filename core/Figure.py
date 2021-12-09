
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

import plotly
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Figure:
    def __init__(self):
        self.figure = None

    def CandleStick(self, df):
        # Create candlestick
        self.figure = go.Figure(dict({
            "data":
                [go.Candlestick(
                    x = df.index,
                    open = df['open'],
                    high = df['high'],
                    low = df['low'],
                    close = df['close']
                )],
            "layout": {
                "title": {
                    "text": "Temp name",
                }
            }
        }))


    def AppendCandles(self, df):
        if not self.figure:
            self.CandleStick(df)
        else:
            self.figure.add_vline(x=df.index[0], line_width=2, line_dash="dash", line_color="grey")
            self.figure['data'][0]['x'] = np.concatenate((self.figure['data'][0]['x'],df.index))
            self.figure['data'][0]['open'] = np.concatenate((self.figure['data'][0]['open'],df.open))
            self.figure['data'][0]['high'] = np.concatenate((self.figure['data'][0]['high'],df.high))
            self.figure['data'][0]['low'] = np.concatenate((self.figure['data'][0]['low'],df.low))
            self.figure['data'][0]['close'] = np.concatenate((self.figure['data'][0]['close'],df.close))


    def AddMarker(self, x, y, symbol, color, output="", size=20):
        # Add to figure
        self.figure.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text',
                text=output,
                textposition='top right',
                marker=plotly.graph_objs.scatter.Marker(size=size,
                                 symbol=symbol,
                                 color=color)
            )
        )

    def AddStopLine(self, start, end, price):
        self.figure.add_shape(type="line", x0=start,
            y0 = price,
            x1 = end,
            y1 = price, fillcolor = 'yellow')

    def AddLine(self, df, column, color="black", name="Undefined", width=1):
        self.figure.add_trace(
            go.Scatter(
                x=df.index,
                y=df[column],
                line=dict(color=color, width=width)
            )
        )

    def TextConfig(self, chartTitle="Stock Prices", height=1200, width=2560,  yaxis="Price $ - US Dollars"):
        # Update figure
        self.figure.update_layout(
            title=chartTitle,
            height=height,
            width=width,
            dragmode= 'zoom',
            showlegend=False,
            yaxis=dict(title=yaxis),
            xaxis=dict(type="category", rangeslider_visible=False)
        )

    def AddVerticalRect(self, x0, x1, color):
        self.figure.add_vrect(
            x0=x0,
            x1=x1,
            line_width=50,
            fillcolor=color,
            opacity=0.5
        )

    def Show(self):
        self.figure.show()

    def Save(self, path):
        self.figure.write_image(path)
