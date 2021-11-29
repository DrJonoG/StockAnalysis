
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
import sys
import inspect
import pandas as pd
# Setup
currentDir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentDir = os.path.dirname(currentDir)
sys.path.insert(0, parentDir)
# Import custom
import core.ComputeIndicators as CI

if __name__ == '__main__':
    # Clear screen prior to execution
    clear = lambda: os.system('cls')
    clear()

    # Inidcator varialbles
    source = 'D:/00.Stocks/data/alpha/5m/'
    destination = 'D:/00.Stocks/indicators/alpha/5m/'
    indicators = {
        'expMovingAverage': [3, 5, 10, 20, 50, 100],
        'simpleMovingAverage': [5, 10, 20, 50, 100],
        'rsiLength': 14,
        'bollingerPeriod': 20,
        'bollingerStdDev': 1.5,
        'vWAP': True,
        'precision': 2
    }

    # Indicator Initialise
    symbolIndicators = CI.ComputeIndicators(**indicators)
    # Compute indicators on variable
    symbolIndicators.Compute(source, destination, marketOnly=False)
