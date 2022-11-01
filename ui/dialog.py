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

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt6.QtGui import QStandardItemModel

from ui.raw.ui_dialog import Ui_Dialog


class DialogWindow(QDialog, Ui_Dialog):
    def __init__(self):
        super(DialogWindow, self).__init__()
        self.setupUi(self)

        model = QStandardItemModel()
        self.tableView.setModel(model)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        # It's connecting the buttons to their respective methods.
        self.importButton.clicked.connect(self.importData)
        self.saveButton.clicked.connect(self.saveData)
        self.deleteButton.clicked.connect(self.deleteRow)

    def importData(self):
        """
        It's opening a file dialog and getting the path of the file that the user selected. It's importing the data from the
        file into the tableView.
        """
        print("importData")
        # It's opening a file dialog and getting the path of the file that the user selected.
        path, _filter = QFileDialog.getOpenFileName(self, 'Import File', '', 'CSV(*.csv)')
        filename = path
        # It's importing the data from the file into the tableView.
        if filename != "":
            with open(filename, "r") as fileInput:
                # It's reading the file and adding the data to the tableView.
                for row in csv.reader(fileInput):
                    items = [
                        QtGui.QStandardItem(field)
                        for field in row
                    ]
                    # It's adding a row to the tableView.
                    self.tableView.model().appendRow(items)

    def saveData(self):
        """
        It's iterating through the rows and columns of the tableView and
        writing the data to a csv file.
        """
        print("save")
        filename = self.filePath.text()
        # It's opening a file dialog and getting the path of the file that the user selected.
        if filename == "":
            path, _filter = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV(*.csv)')
            filename = path
        # It's opening the file and creating a writer object.
        if filename != "":
            self.filePath.setText(filename)
            csvf = open(filename, 'w', newline='')
            writer = csv.writer(csvf, csv.excel)
            # It's iterating through the rows of the tableView and adding the data to the rowdata list.
            for row in range(self.tableView.model().rowCount()):
                rowdata = []
                # It's iterating through the columns of the tableView and adding the data to the rowdata list.
                for column in range(self.tableView.model().columnCount()):
                    item = self.tableView.model().item(row, column)
                    # It's checking if the item is not None. If the item is not None, it's adding the item to the rowdata
                    # list.
                    if item is not None:
                        rowdata.append(item.text().strip())
                writer.writerow(rowdata)

    def deleteRow(self, filename):
        """
        It removes all the rows from the tableView
        :param filename: the name of the file to be deleted
        """
        print("del")
        self.tableView.model().removeRows(0, self.tableView.model().rowCount())

    def loadData(self, filename):
        """
        It's iterating through the rows of the file and adding the data to the tableView
        :param filename: The name of the file to open
        """
        with open(filename, "r") as fileInput:
            # It's iterating through the rows of the file and adding the data to the tableView.
            for row in csv.reader(fileInput):
                items = [
                    QtGui.QStandardItem(field.strip())
                    for field in row
                ]
                # for field in row
                # for i in range(len(row)) if i > 2
                # if row[3].lower().find("cgi") > -1:
                self.tableView.model().appendRow(items)
