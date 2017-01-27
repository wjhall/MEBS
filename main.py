# todo:
#   select categories in transaction view
#   add budget view


import sqlite3
import pandas as pd
import sys
from PySide.QtCore import *
from PySide.QtGui import *
from QIF_Handler import *
from SQL_Handler import *
from functools import partial
import os.path


class MEBS(QMainWindow):

    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.db = ""
        if os.path.isfile(self.path + "\config.ini"):
            with open(self.path + "\config.ini") as f:
                self.db = f.readline()
        self.selectedAcc = '%'
        QMainWindow.__init__(self)
        if self.db == "":
            self.drawLoad()
        else:
            self.drawHome()

    def drawLoad(self):
        self.setupMenuBar()

        self.main = QWidget(self)
        self.main.setMinimumSize(800, 600)

        self.layout = QHBoxLayout()
        button = (QPushButton("New"))
        button.clicked.connect(self.newDB)
        self.layout.addWidget(button)
        button = (QPushButton("Load"))
        button.clicked.connect(self.loadDB)
        self.layout.addWidget(button)
        self.main.setLayout(self.layout)
        self.setCentralWidget(self.main)
        self.show()

    def updateTransTable(self, account):
        self.selectedAcc = account
        self.drawHome()

    def drawHome(self):
        self.setupMenuBar()

        self.main = QWidget(self)
        self.main.setMinimumSize(800, 600)

        self.TransTable = dfToQTab(getTransSQL(self.selectedAcc, self.db))

        self.AccBox = QGroupBox("Accounts", self.main)
        self.AccBox.setLayout(self.AccountsListVBox())

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.AccBox)
        self.layout.addWidget(getTabBar(self))
        self.main.setLayout(self.layout)

        self.setCentralWidget(self.main)
        self.show()

    def loadDB(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        filename = dialog.getOpenFileName(filter="*.db")
        if filename[0] == "":
            return
        self.db = filename[0]
        self.setConfig()
        self.drawHome()

    def newDB(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        filename = dialog.getSaveFileName(filter="*.db")
        if filename[0] == "":
            return
        self.db = filename[0]
        initTransTable(self.db)
        initAccTable(self.db)
        initEnvelopesTable(self.db)
        initBudgetTable(self.db)
        self.setConfig()
        self.drawHome()

    def setupMenuBar(self):
        menu = QMenuBar()
        newmenu = QAction('New', self)
        newmenu.triggered.connect(self.newDB)
        menu.addAction(newmenu)
        loadmenu = QAction('Load', self)
        loadmenu.triggered.connect(self.loadDB)
        menu.addAction(loadmenu)
        QIFImport = QAction('Import QIF', self)
        QIFImport.triggered.connect(self.importQIF)
        menu.addAction(QIFImport)
        quitmenu = QAction('Quit', self)
        quitmenu.triggered.connect(QApplication.quit)
        menu.addAction(quitmenu)
        self.setMenuBar(menu)

    def AccountsListVBox(self):
        vbox = QVBoxLayout()
        for account in getAccounts(self.db):
            button = (QPushButton(account[0]))
            button.clicked.connect(partial(self.updateTransTable, account[0]))
            label = (QLabel(str(account[1])))
            vbox.addWidget(button)
            vbox.addWidget(label)
        button = (QPushButton("Add New Account"))
        button.clicked.connect(self.newAccount)
        vbox.addWidget(button)
        vbox.setAlignment(Qt.AlignTop)
        return vbox

    def newAccount(self):
        account = QInputDialog.getText(self, "Add New Account", "Account Name")
        self.selectedAcc = account[0]
        addAccountSQL(self.selectedAcc, 'foo', self.db)
        self.drawHome()

    def setConfig(self):
        with open(self.path + "\config.ini", 'w+') as f:
            f.write(self.db)

    def importQIF(self):
        accountlist = [acc[0] for acc in getAccounts(self.db)]
        account = QInputDialog.getItem(self, "Select account to import to", "Account", accountlist)
        self.selectedAcc = account[0]
        filename = QFileDialog.getOpenFileName(self)
        if filename[0] == "":
            return
        qif = readQif(filename[0], self.selectedAcc)
        insertTransSQL(qif, self.db)
        updateAccSQLBalance(self.db)
        self.drawHome


def getTabBar(parent):
    tabs = QTabWidget(parent)
    tabs.addTab(parent.TransTable, "Transactions")
    tabs.addTab(QLabel("foo"), "Budget")
    tabs.addTab(QLabel("foo"), "Reports")
    return tabs


def dfToQTab(df):
    datatable = QTableWidget()
    datatable.setColumnCount(len(df.columns))
    datatable.setRowCount(len(df.index))
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            datatable.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
    datatable.setHorizontalHeaderLabels(df.columns)
    return datatable


if __name__ == "__main__":
    app = QApplication(sys.argv)
    UI = MEBS()
    app.exec_()
    sys.exit()
