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
        It opens a file dialog, gets the file path, opens the file, reads the file, and then appends the data to the table
        view
        """
        path, _filter = QFileDialog.getOpenFileName(self, 'Import File', '', 'CSV(*.csv)')
        filename = path
        if filename != "":
            with open(filename, "r") as fileInput:
                for row in csv.reader(fileInput):
                    items = [
                        QtGui.QStandardItem(field)
                        for field in row
                    ]
                    self.tableView.model().appendRow(items)

    def saveData(self):
        """
        It opens a file dialog to get a file name, then opens a file with that name, then writes the contents of the table
        to the file
        """
        filename = self.filePath.text()
        if filename == "":
            path, _filter = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV(*.csv)')
            filename = path
        if filename != "":
            self.filePath.setText(filename)
            csvf = open(filename, 'w', newline='')
            writer = csv.writer(csvf, csv.excel)
            for row in range(self.tableView.model().rowCount()):
                rowdata = []
                for column in range(self.tableView.model().columnCount()):
                    item = self.tableView.model().item(row, column)
                    if item is not None:
                        rowdata.append(item.text().strip())
                writer.writerow(rowdata)

    def deleteRow(self):
        """
        It removes all the rows from the table view
        """
        self.tableView.model().removeRows(0, self.tableView.model().rowCount())

    def loadData(self, filename):
        """
        It opens the file, reads the file, and then appends the data to the tableView

        :param filename: The name of the file to load
        """
        with open(filename, "r") as fileInput:
            for row in csv.reader(fileInput):
                items = [
                    QtGui.QStandardItem(field.strip())
                    for field in row
                ]
                self.tableView.model().appendRow(items)
