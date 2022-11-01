import csv
import subprocess
import sys

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow

from dialog import Ui_Dialog
from mainWindow import Ui_MainWindow
from log import Log
from shellshockScanner import CGIBugScanner


class DialogWindow(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(DialogWindow, self).__init__(parent)
        self.setupUi(self)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.dialog = DialogWindow(self)
        self.actionOpenDB.triggered.connect(self.openDB)
        self.actionStartScanning.triggered.connect(self.startScanning)
        self.actionClearConsole.triggered.connect(self.clearConsole)
        Log.instance(self.getTextEdit()).out("Start")
        self.getTextEdit().clear()

    def openDB(self):
        """
        The function opens a dialog box and loads a file called cgi_list.txt into the dialog box
        """
        self.dialog.show()
        self.dialog.loadData("cgi_list.txt")#cgi.csv"cgi_list.txt"

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec())
