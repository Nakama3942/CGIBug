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

        self.actionOpenDB.triggered.connect(self.openDB)
        self.actionStartScanning.triggered.connect(self.startScanning)
        self.actionClearConsole.triggered.connect(self.clearConsole)

        Log.instance(self.getTextEdit()).out("Start")
        self.getTextEdit().clear()

    def openDB(self):
        """
        The function opens a dialog box and loads a file called cgi_list.txt into the dialog box
        """
        self.dialog = DialogWindow()
        self.dialog.show()
        self.dialog.loadData("cgi_list.txt")  # cgi.csv"cgi_list.txt"

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
        return self.textEdit
