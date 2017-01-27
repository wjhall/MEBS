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
        self.db = ""
        self.selectedAcc = '%'
        QMainWindow.__init__(self)
        self.drawLoad()

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
        self.AccBox.setLayout(AccountsListVBox(self))

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
        QIFImport.triggered.connect(lambda: importQIF(self))
        menu.addAction(QIFImport)
        quitmenu = QAction('Quit', self)
        quitmenu.triggered.connect(QApplication.quit)
        menu.addAction(quitmenu)
        self.setMenuBar(menu)


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
    vbox.setAlignment(Qt.AlignTop)
    return vbox

app = QApplication(sys.argv)
UI = MEBS()
app.exec_()
sys.exit()
