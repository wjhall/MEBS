# todo:
#   fix budget view by month
#   capacity to edit budget items
#   capacity to delete transactions
#   capacity to highlight/filter transactions by category
#   add reports


import sqlite3
import pandas as pd
import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtSql import *
from QIF_Handler import *
from SQL_Handler import *
from Widget_Handler import *
from functools import partial
import os.path


class MEBS(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        with open('C:\Users\whall\Documents\dev\MEBS\MEBS\MEBS\Style.css', 'r') as file:
            style_sheet = file.read()
            self.setStyleSheet(style_sheet)
        self.path = os.path.dirname(__file__)
        self.WH = Widget_Handler(self)
        if os.path.isfile(self.path + "\config.ini"):
            with open(self.path + "\config.ini") as f:
                self.SQL = SQL_Handler(f.readline(), self)
                self.drawHome()
        else:
            self.drawLoad()

    def drawLoad(self):
        self.WH.setupMenuBar()

        self.main = QWidget(self)
        self.main.setMinimumSize(800, 600)

        self.layout = QHBoxLayout()
        button = (QPushButton("New"))
        button.clicked.connect(partial(self.loadDB, True))
        self.layout.addWidget(button)
        button = (QPushButton("Load"))
        button.clicked.connect(self.loadDB)
        self.layout.addWidget(button)
        self.main.setLayout(self.layout)
        self.setCentralWidget(self.main)
        self.show()

    def updateTransTable(self, account):
        self.SQL.setSelectedAcc(account)
        self.drawHome()

    def drawHome(self):
        self.WH.setupMenuBar()

        self.main = QWidget(self)
        self.main.setMinimumSize(800, 600)

        self.AccBox = QGroupBox("Accounts", self.main)
        self.AccBox.setLayout(self.WH.AccountsListVBox())

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.AccBox)
        self.layout.addWidget(self.WH.getTabBar())
        self.main.setLayout(self.layout)

        self.setCentralWidget(self.main)
        self.show()

    def loadDB(self, new=False):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        if new:
            filename = dialog.getSaveFileName(filter="*.db")
        else:
            filename = dialog.getOpenFileName(filter="*.db")
        if filename[0] == "":
            return
        self.SQL = SQL_Handler(filename[0], self)
        if new:
            self.SQL.initNewDB()
        self.setConfig()
        self.drawHome()

    def newAccount(self):
        name = QInputDialog.getText(self, "Add New Account", "Account Name")
        if name[0] == "":
            self.drawHome()
            return
        self.SQL.addAccount(name[0])
        self.drawHome()

    def setConfig(self):
        with open(self.path + "\config.ini", 'w+') as f:
            f.write(self.SQL.dbpath)

    def importQIF(self):
        accountlist = [acc[0] for acc in self.SQL.getAccounts()]
        account = QInputDialog.getItem(self, "Select account to import to", "Account", accountlist)
        self.SQL.setSelectedAcc(account[0])
        dialog = QFileDialog(self)
        filename = dialog.getOpenFileName(filter="*.qif")
        if filename[0] == "":
            return
        self.SQL.insertTransSQL(filename[0])
        self.drawHome()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UI = MEBS()
    app.exec_()
    sys.exit()
