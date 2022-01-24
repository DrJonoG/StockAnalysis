
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
import configparser
import core.GetData as getData
from helpers import SymbolIterator

if __name__ == '__main__':
    destination = './config/fundamental.csv'

    # Clear screen prior to execution
    clear = lambda: os.system('cls')
    clear()

    # Config
    config = configparser.ConfigParser()
    config.read('./config/source.ini')

    # Config
    symbolFileList = config['filepath']['symbolList']

    # Data object
    data = getData.GetData('./config/api.conf')

    # Delete existing file
    if os.path.exists(destination):
        os.remove(destination)

    # Iterate
    SymbolIterator([symbolFileList], data.Downloadfundamental, [destination], apiCap=100, functionCalls=1)
