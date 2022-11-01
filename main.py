import sys

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication

from ui.bugger import CGIBug


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = CGIBug()
    ui.show()
    sys.exit(app.exec())
