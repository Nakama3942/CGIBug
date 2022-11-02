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

import csv
import subprocess
import sys

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow

from ui.raw.ui_bugger import Ui_CGIBug
from ui.dialog import DialogWindow
from src.log import Log
from src.shellshockScanner import CGIBugScanner


class CGIBug(QMainWindow, Ui_CGIBug):
    def __init__(self):
        super(CGIBug, self).__init__()
        self.setupUi(self)

        # It's a declaration of other windows of the program
        self.dialog = None

        # It's a tracking of button clicks in the window
        self.actionOpenDB.triggered.connect(self.openDB)
        self.actionStartScanning.triggered.connect(self.startScanning)
        self.actionClearConsole.triggered.connect(self.clearConsole)

        Log.instance(self.getTextEdit()).out("Start")
        self.getTextEdit().clear()

    def openDB(self):
        """
        It opens a dialog window, shows it, and loads data from a file
        """
        self.dialog = DialogWindow()
        self.dialog.show()
        self.dialog.loadData("cgi_list.txt")

    def startScanning(self):
        """
        It takes a list of hosts and a list of CGI scripts and scans them for vulnerabilities
        """
        Log.out("Start scanning")
        scanner = CGIBugScanner()
        scanner.main("host_list.txt", "cgi_list.txt", "log.csv")
        Log.out("Scanning finished")

    def clearConsole(self):
        """
        It clears the text in the textEdit widget
        """
        self.getTextEdit().clear()

    def getTextEdit(self):
        """
        It returns the textEdit object
        :return: The textEdit object is being returned.
        """
        return self.textEdit
