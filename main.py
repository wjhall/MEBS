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
from functools import partial
import os.path


class MEBS(QMainWindow):

    def __init__(self):
        self.path = os.path.dirname(__file__)
        self.db = ""
        if os.path.isfile(self.path + "\config.ini"):
            with open(self.path + "\config.ini") as f:
                self.db = f.readline()
        self.selectedAcc = 0
        QMainWindow.__init__(self)
        if self.db == "":
            self.drawLoad()
        else:
            self.openDB()
            self.drawHome()

    def openDB(self):
        self.tempdb = QSqlDatabase.addDatabase("QSQLITE")
        self.tempdb.setDatabaseName(self.db)
        self.tempdb.open()

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
        if account == 0:
            self.selectedAcc = 0
        else:
            self.selectedAcc = accountID(self, account)
        self.drawHome()

    def drawHome(self):
        self.setupMenuBar()

        self.main = QWidget(self)
        self.main.setMinimumSize(800, 600)

        self.AccBox = QGroupBox("Accounts", self.main)
        self.AccBox.setLayout(self.AccountsListVBox())

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.AccBox)
        self.layout.addWidget(self.getTabBar())
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
        self.openDB()
        self.setConfig()
        self.drawHome()

    def newDB(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        filename = dialog.getSaveFileName(filter="*.db")
        if filename[0] == "":
            return
        self.db = filename[0]
        self.openDB()
        initNewDB(self)
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
        for account in getAccounts(self):
            button = QPushButton(account[0])
            button.clicked.connect(partial(self.updateTransTable, account[0]))
            label = QLabel(str(account[1]))
            vbox.addWidget(button)
            vbox.addWidget(label)
        button = QPushButton("All Accounts")
        button.clicked.connect(partial(self.updateTransTable, 0))
        label = QLabel(str(sum(account[1] for account in getAccounts(self))))
        vbox.addWidget(button)
        vbox.addWidget(label)
        button = QPushButton("Add New Account")
        button.clicked.connect(self.newAccount)
        vbox.addWidget(button)
        vbox.setAlignment(Qt.AlignTop)
        return vbox

    def newAccount(self):
        account = QInputDialog.getText(self, "Add New Account", "Account Name")
        addAccountSQL(account[0], 'foo', self)
        self.selectedAcc = accountID(self, account[0])
        self.drawHome()

    def setConfig(self):
        with open(self.path + "\config.ini", 'w+') as f:
            f.write(self.db)

    def importQIF(self):
        accountlist = [acc[0] for acc in getAccounts(self)]
        account = QInputDialog.getItem(self, "Select account to import to", "Account", accountlist)
        self.selectedAcc = accountID(self, account[0])
        dialog = QFileDialog(self)
        filename = dialog.getOpenFileName(filter="*.qif")
        if filename[0] == "":
            return
        insertTransSQL(filename[0], self)
        updateAccSQLBalance(self)
        self.drawHome()

    def getTransTable(self):
        self.Tmodel = QSqlRelationalTableModel()
        self.Tmodel.setTable("Transactions")
        self.Tmodel.setRelation(7, QSqlRelation("Envelopes", "ID", "subcategory"))
        self.Tmodel.setRelation(2, QSqlRelation("Accounts", "ID", "Name"))
        self.Tmodel.setEditStrategy(QSqlTableModel.OnRowChange)
        if self.selectedAcc != 0:
            self.Tmodel.setFilter("account={}".format(self.selectedAcc))
        self.Tmodel.select()
        view = QTableView()
        view.setModel(self.Tmodel)
        view.setItemDelegate(QSqlRelationalDelegate(view))
        view.setColumnHidden(0, True)
        return view

    def getBudgetTable(self):
        self.Bmodel = QSqlQueryModel()
        sql = "Select Envelopes.category, Envelopes.subcategory, foo.Total\
            FROM Envelopes \
            LEFT OUTER JOIN ( \
                SELECT category, sum(amount) as Total \
                FROM Transactions \
                WHERE TransDate > '2016-12-31' \
                GROUP BY category\
            ) as foo \
            ON Envelopes.ID = foo.category \
            GROUP BY Envelopes.subcategory \
            ORDER BY Envelopes.category, Envelopes.subcategory"
        self.Bmodel.setQuery(sql)
        view = QTableView()
        view.setModel(self.Bmodel)
        return view

    def getTabBar(self):
        tabs = QTabWidget(self)

        topLayout = QVBoxLayout()
        topLayout.addWidget(self.getTransTable())

        bottomLayout = QHBoxLayout()
        button = QPushButton("Add Transaction")
        button.clicked.connect(partial(self.Tmodel.insertRow, 1))
        bottomLayout.addWidget(button)
        button = QPushButton("Save Changes")

        def saveChanges():
            self.Tmodel.submitAll()
            updateAccSQLBalance(self)
            self.drawHome()
        button.clicked.connect(saveChanges)
        bottomLayout.addWidget(button)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(bottomLayout)

        transWidg = QWidget(self)
        transWidg.setLayout(mainLayout)
        tabs.addTab(transWidg, "Transactions")

        tabs.addTab(self.getBudgetTable(), "Budget")
        tabs.addTab(QLabel("foo"), "Reports")
        return tabs


if __name__ == "__main__":
    app = QApplication(sys.argv)
    UI = MEBS()
    app.exec_()
    sys.exit()
