#  Copyright © 2022 Kalynovsky Valentin. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os


class Log:
    _file = None
    _instance = None
    _editor = None

    def __init__(self, file, editor=None):
        self._file = open(file, 'w+')
        self._editor = editor

    @staticmethod
    def instance(editor=None):
        """
        If the Log class has no instance, create one and return it

        :param editor: The editor to use to open the log file
        :return: The instance of the Log class.
        """
        if Log._instance is None:
            filename = 'log.txt'
            try:
                os.remove(filename)
            except OSError:
                pass
            Log._instance = Log(filename, editor)
        return Log._instance

    @staticmethod
    def out(text):
        """
        It prints the text to the console and to the log file

        :param text: The text to be written to the log file
        """
        print(text)
        Log.instance()._file.write(text + "\n")
        if Log.instance()._editor is not None:
            Log.instance()._editor.append(text)
