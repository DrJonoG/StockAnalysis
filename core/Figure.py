
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
        self.figure = make_subplots(specs=[[{"secondary_y": True}]])

        self.figure.add_trace(go.Candlestick(x=df.index.time,
                                    open=df['open'], high=df['high'],
                                    low=df['low'], close=df['close'],
                                    increasing_line_color= 'black', decreasing_line_color= 'black', opacity=0.8,
                                    name='Day', yaxis='y'
                                  )
                   )

        self.figure.data[0].decreasing.fillcolor = 'black'
        self.figure.data[0].increasing.fillcolor = 'white'

        self.figure.add_trace(go.Bar(x=df.index.time, y=df['volume'],
                          name='Volume', opacity=0.1, marker_color='#778899',
                          yaxis='y2'
                          )
                   )

        self.figure.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        self.figure.update_layout(margin=dict(l=5, r=5, t=5, b=5))
        #self.figure.add_trace(go.Bar(x=df.index,y=df[‘volume’]),row=2,col=1)
        #self.figure = make_subplots(specs=[[{"secondary_y": True}]])
        #self.figure.add_trace(go.Bar(x=df.index, y=df['volume']), secondary_y=False)


    def AppendCandles(self, df):
        if not self.figure:
            self.CandleStick(df)
        else:
            self.figure.add_vline(x=df.index[0].time, line_width=2, line_dash="dash", line_color="grey")
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


    def AddStopLine(self, end, start, price, output, col='black',width=1):
        self.figure.add_trace(
            go.Scatter(
                x=[start,end],
                y=[price, price],
                mode='lines',
                line=dict(color=col, width=width)
            )
        )
        self.figure.add_trace(go.Scatter(x=[end], y=[price], textposition='top right', text=output, mode="text", showlegend=False))

    def AddLine(self, df, column, color="black", name="Undefined", width=1,output=""):
        self.figure.add_trace(
            go.Scatter(
                x=df.index.time,
                y=df[column],
                mode='lines+text',
                text=output,
                textposition='top right',
                line=dict(color=color, width=width)
            )
        )

    def addText(self, preh, prel, yhigh, ylow):
        # add annotation
        self.figure.add_annotation(
            xref='x domain',
            yref='y domain',
            x=0.03,
            y=0.9,
            text='YHigh: ' + str(yhigh) + '<br />YLow: ' + str(ylow) + '<br />PHigh: ' + str(preh) + '<br />PLow: ' + str(prel),
            showarrow=False,
            row=1, col=1
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
            line_width=10,
            fillcolor=color,
            opacity=0.5
        )

    def AddSlope(self, x1, x2, y1, y2, slope):
        self.figure.add_trace(
            go.Scatter(
                mode='lines+text',
                textposition='top right',
                text = str(round(slope,2)),
                x=[x1, x2],
                y=[y1, y2],
                line=dict(color="blue", width=1)
            )
        )

    def Show(self):
        self.figure.show()

    def Save(self, path):
        self.figure.write_image(path)
