from PySide.QtCore import *
from PySide.QtGui import *
from functools import partial
import datetime
from dateutil.relativedelta import relativedelta

class Widget_Handler():

    def __init__(self, parent):
        self.parent = parent

    def setupMenuBar(self):
        menu = QMenuBar()
        newmenu = QAction('New', self.parent)
        newmenu.triggered.connect(partial(self.parent.loadDB, True))
        menu.addAction(newmenu)
        loadmenu = QAction('Load', self.parent)
        loadmenu.triggered.connect(self.parent.loadDB)
        menu.addAction(loadmenu)
        QIFImport = QAction('Import QIF', self.parent)
        QIFImport.triggered.connect(self.parent.importQIF)
        menu.addAction(QIFImport)
        quitmenu = QAction('Quit', self.parent)
        quitmenu.triggered.connect(QApplication.quit)
        menu.addAction(quitmenu)
        self.parent.setMenuBar(menu)

    def AccountsListVBox(self):
        vbox = QVBoxLayout()
        for account in self.parent.SQL.getAccounts():
            button = QPushButton(account[0])
            button.clicked.connect(partial(self.parent.updateTransTable, account[0]))
            label = QLabel(str(account[1]))
            vbox.addWidget(button)
            vbox.addWidget(label)
        button = QPushButton("All Accounts")
        button.clicked.connect(partial(self.parent.updateTransTable, 0))
        label = QLabel(str(sum(account[1] for account in self.parent.SQL.getAccounts())))
        vbox.addWidget(button)
        vbox.addWidget(label)
        button = QPushButton("Add New Account")
        button.clicked.connect(self.parent.newAccount)
        vbox.addWidget(button)
        vbox.setAlignment(Qt.AlignTop)
        return vbox

    def getTabBar(self):
        tabs = QTabWidget(self.parent)

        tabs.addTab(self.TransTab(), "Transactions")
        tabs.addTab(self.BudgetTab(), "Budget")
        tabs.addTab(QLabel("foo"), "Reports")
        return tabs

    def TransTab(self):
        topLayout = QVBoxLayout()
        self.parent.SQL.getTransTable()
        topLayout.addWidget(self.parent.Tview)

        bottomLayout = QHBoxLayout()
        button = QPushButton("Add Transaction")
        button.clicked.connect(partial(self.parent.Tmodel.insertRow, 1))
        bottomLayout.addWidget(button)

        button = QPushButton("Save Changes")

        def saveChanges():
            self.parent.Tmodel.submitAll()
            self.parent.SQL.updateAccSQLBalance()
            self.parent.SQL.updateBudgetValues()
            self.parent.drawHome()
        button.clicked.connect(saveChanges)
        bottomLayout.addWidget(button)

        button = QPushButton("Delete Row")

        def delRow():
            rows = sorted(set(index.row() for index in
                              self.parent.Tview.selectedIndexes()))
            for row in rows:
                self.parent.Tmodel.removeRow(row)
            self.parent.SQL.updateAccSQLBalance()
            self.parent.drawHome()
        button.clicked.connect(delRow)
        bottomLayout.addWidget(button)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(bottomLayout)

        transWidg = QWidget(self.parent)
        transWidg.setLayout(mainLayout)
        return transWidg

    def BudgetTab(self):
        def ChangeMonth(n):
            current = self.parent.SQL.selectedMonth
            current = datetime.datetime.strptime(current, "%Y-%m")
            current += relativedelta(months=n)
            self.parent.SQL.selectedMonth = current.strftime("%Y-%m")
            self.parent.drawHome()

        topLayout = QVBoxLayout()
        self.parent.SQL.getBudgetTable()
        topLayout.addWidget(self.parent.Bview)

        bottomLayout = QHBoxLayout()

        button = QPushButton("Previous Month")
        button.clicked.connect(partial(ChangeMonth, -1))
        bottomLayout.addWidget(button)
        button = QPushButton("Next Month")
        button.clicked.connect(partial(ChangeMonth, +1))
        bottomLayout.addWidget(button)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(bottomLayout)

        BudWidg = QWidget(self.parent)
        BudWidg.setLayout(mainLayout)
        return BudWidg
