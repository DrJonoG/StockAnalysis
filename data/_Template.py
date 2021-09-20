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

class Template:
    def __init__(self):
        print("==> Datasource set to <> \n")

    def Download(self, symbol, dataRange, dataInterval):
        """
	    Downloads data for a single symbol
        Returns: a dataframe ordered datetime, open, close, high, low, volume
        
        Parameters
        ----------
        symbol : String
            The symbol which to obtain quote data for
        dataRange : String
            The range (i.e. 60d) for which to obtain data
        dataInterval : String
            The time period for which to obtain data (i.e. 5m)
        """

        pass


    def Update(self, symbol, dataInterval, sourcePath):
        """
	    Update a single symbol

        Parameters
        ----------
        symbol : String
            The name of the symbol to update
        dataInterval : String
            The time period for which to obtain data (i.e. 5m)
        sourcePath : String:
            Where the master files are to update
        """

        # Confirm file does exist
        if not os.path.exists(sourcePath):
            return "Error: No files found"
