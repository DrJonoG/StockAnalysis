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

import pandas as pd

class Gaps(object):
    def __init__(self, change, prev, curr):
        self.change = change
        self.previousDF = prev
        self.currentDF = curr

class Gappers:
    def __init__(self, visual=False):
        self.visual = visual

    def GroupBy(self, df, group='D'):
        groups = [g for n, g in df.groupby(pd.Grouper(freq=group))]
        return [i for i in groups if len(i)>0]

    def Gaps(self, groups, percent):
        # Error checking
        if percent > 1 or percent < -1:
            raise ValueError("==> Error: Invalid percent. Must be between 1 and -1")
        if not groups:
            self.GroupBy()

        gaps = []
        # Skip the first group so we can look back
        for index, group in enumerate(groups[1:], start=1):
            open = group['open'].iloc[0]
            close = groups[index-1]['close'].iloc[-1]
            change = ((open - close) / close)
            if change >= percent or change <= percent * -1:
                gaps.append(Gaps(round(change, 5), groups[index-1], group))
        return gaps

    def Analysis(self, gap):
        if gap.change > 0:
            # Get the close and open
            prevDayClose = gap.previousDF['close'].iloc[-1]
            currDayOpen = gap.currentDF['open'].iloc[0]
            # The difference between the open in the current bar and close in the previous
            openCloseChange = round(currDayOpen - prevDayClose, 2)
            # Get the minimum and maximum close of the current day
            closeMin =  round(min(gap.currentDF['close']),2)
            closeMax = round(max(gap.currentDF['close']),2)
            # Get the minimum and maximum  of the current day
            highOfDay =  round(max(gap.currentDF['high']),2)
            minOfDay = round(min(gap.currentDF['low']),2)
            # Difference between high and low of day
            HLDiff = round(closeMax - closeMin, 2)
            # Different between the minimum of the day and open of the day
            diffCurrDown = round(closeMin - currDayOpen, 2)
            # Difference between the open today and close yesterday
            diffCurrUp = round(currDayOpen - prevDayClose, 2)
            # Difference between the min and max today and the close yesterday
            diffDown = round(closeMin - prevDayClose, 2)
            diffUp = round(closeMax - prevDayClose, 2)
            # Has the gap been filled
            gapFill = (diffDown < 0)
            # The bar in which the gap was filled
            barBroken = 'N/A'
            if gapFill:
                for j in range(len(gap.currentDF)):
                    if gap.currentDF['close'].iloc[j] <= prevDayClose:
                        barBroken = j
                        break
            # Output # Todo save to csv
            print("------------------------------")
            print("Close: $%s " % str(prevDayClose))
            print("Open: $%s\n " % str(currDayOpen))
            print("Gap Up ($): %s" % str(openCloseChange))
            print("Gap Up: %s\n" % (str(round(gap.change*100, 2)) + '%'))
            print("High of day $%s" % str(closeMax))
            print("Diff to Prev Close: $%s " % str(diffUp))
            print("Diff to Curr Open: $%s\n " % str(diffCurrUp))
            print("Low of day: $%s" % str(closeMin))
            print("Diff to Prev Close: $%s " % str(diffDown))
            print("Diff to Curr Open: $%s\n " % str(diffCurrDown))
            print("ATR Current Day: $%s" % str(HLDiff))
            print("Gap filled: %s " % gapFill)
            print("Gap filled at: %s" % str(barBroken))


    def AnalyseGaps(self, path, group, minPercent):
        df = pd.read_csv(path, index_col=0)
        df.index = pd.to_datetime(df.index)
        # Group the data by specified group (H, D, W, M, Y)
        groupedDF = self.GroupBy(df, group)
        # Store all gaps less than -1* percent and greater than 1*percent
        gaps = self.Gaps(groupedDF, minPercent)
        # Analyse gaps
        for gap in gaps:
            self.Analysis(gap)
