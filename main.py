import sqlite3
import pandas as pd
import sys
from PySide.QtCore import *
from PySide.QtGui import *
from QIF_Handler import *
from SQL_Handler import *
from functools import partial


class MEBS(QMainWindow):

    def __init__(self):
        self.db = "C:\Users\whall\Documents\dev\MEBS\python\mydb.db"
        QMainWindow.__init__(self)
        menu = getMenuBar(self)
        self.TransTable = dfToQTab(getTransSQL('123std2', self.db))

        self.setMenuBar(menu)

        self.main = QWidget(self)

        self.AccBox = QGroupBox("Accounts", self.main)
        self.AccBox.setLayout(AccountsListVBox(self))

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.AccBox)
        self.layout.addWidget(getTabBar(self))
        self.main.setLayout(self.layout)

        self.setCentralWidget(self.main)
        self.show()

    def updateTransTable(self, account):
        print account
        self.TransTable = dfToQTab(getTransSQL(account, self.db))
        self.repaint()


def getMenuBar(parent):
    menu = QMenuBar()
    QIFImport = QAction('Import QIF', parent)
    QIFImport.triggered.connect(lambda: importQIF(parent))
    menu.addAction(QIFImport)
    return menu


def getTabBar(parent):
    tabs = QTabWidget(parent)
    tabs.addTab(parent.TransTable, "Transactions")
    tabs.addTab(QLabel("foo"), "Budget")
    tabs.addTab(QLabel("foo"), "Reports")
    return tabs


def importQIF(parent):
    filename = QFileDialog.getOpenFileName(parent)
    qif = readQif(filename[0], "123std2")
    insertTransSQL(qif, parent.db)


def dfToQTab(df):
    datatable = QTableWidget()
    datatable.setColumnCount(len(df.columns))
    datatable.setRowCount(len(df.index))
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            datatable.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
    datatable.setHorizontalHeaderLabels(df.columns)
    return datatable


def AccountsListVBox(parent):
    vbox = QVBoxLayout()
    conn = sqlite3.connect(parent.db)
    c = conn.cursor()
    sql = "Select * from Accounts"
    c.execute(sql)
    accounts = c
    for account in accounts:
        button = (QPushButton(account[0]))
        button.clicked.connect(partial(parent.updateTransTable, account[0]))
        label = (QLabel(str(account[1])))
        vbox.addWidget(button)
        vbox.addWidget(label)
    return vbox

# initTransTable()
# initAccTable()

# addAccountSQL("123std2")
# TransData = readQif(filename, '123Std')
# insertTransSQL(TransData)

app = QApplication(sys.argv)
UI = MEBS()
app.exec_()
sys.exit()
