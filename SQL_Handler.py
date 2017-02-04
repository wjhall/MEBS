import pandas as pd
from PySide.QtCore import *
from PySide.QtGui import *
from QIF_Handler import *
from PySide.QtSql import *


class SQL_Handler():
    def __init__(self, dbpath, parent):
        self.parent = parent
        self.dbpath = dbpath
        self.selectedAcc = 0
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.dbpath)
        self.db.open()

    def setSelectedAcc(self, account):
        if account == 0:
            self.selectedAcc = 0
        else:
            sql = "SELECT ID from accounts WHERE Name='{}'".format(account)
            query = QSqlQuery(sql, self.db)
            query.first()
            self.selectedAcc = query.value(0)

    def addAccount(self, name):
        sql = "Insert into Accounts (Name, Balance, Type) values ('{}', 0, '{}')".format(name, "foo")
        query = QSqlQuery(sql, self.db)
        self.setSelectedAcc(name)

    def insertTransSQL(self, filename):
        with QIF_Handler() as QIF:
            df = QIF.readQif(filename, self.selectedAcc)
        colList = list(df.columns.values)
        sql = "Insert into Transactions ({}) values ({})"
        headers = ", ".join([i for i in colList])
        blanks = ", ".join(["?" for i in colList])
        sql = sql.format(headers, blanks)
        self.db.transaction()
        query = QSqlQuery(self.db)
        query.prepare(sql)
        for cols in colList:
            query.addBindValue(df[cols].tolist())
        query.execBatch()
        self.db.commit()
        self.updateAccSQLBalance()

    def initNewDB(self):
        sql = '''Create Table if not exists Envelopes (\
            ID integer PRIMARY KEY, \
            category text, \
            subcategory text)'''
        query = QSqlQuery(sql, self.db)
        initevelopes = [
            ["None", "None"],
            ["Expenses", "Housing"],
            ["Expenses", "Groceries"],
            ["Expenses", "Utilities"],
            ["Savings", "Holidays"],
            ["Savings", "EmergencyFund"],
            ["Savings", "ShinyThing"],
        ]
        for envs in initevelopes:
            self.addEnvelope(envs[0], envs[1])
        sql = '''Create Table if not exists Transactions (\
            ID integer PRIMARY KEY, \
            TransDate DATE, \
            account integer, \
            payee text, \
            memo text, \
            cStatus integer, \
            amount real, \
            category integer DEFAULT 1, \
            flags text)'''
        query = QSqlQuery(sql, self.db)
        sql = '''Create Table if not exists Accounts (\
            ID integer PRIMARY KEY, \
            Name text UNIQUE, \
            Balance real, \
            type text)'''
        query = QSqlQuery(sql, self.db)
        sql = '''Create Table if not exists Budget (\
            ID integer PRIMARY KEY, \
            Month Date, \
            subcategory integer, \
            budgeted real, \
            actual real)'''
        query = QSqlQuery(sql, self.db)

    def updateAccSQLBalance(self):
        sql = "Select ID from Accounts"
        query = QSqlQuery(sql, self.db)
        accounts = []
        while query.next():
            accounts.append(query.value(0))
        balances = []
        for account in accounts:
            sql = "Select Sum(amount) from Transactions where account={}".format(account)
            query = QSqlQuery(sql, self.db)
            query.next()
            if query.value(0) != "":
                balance = round(query.value(0), 2)
                balances.append([account, balance])
        for account in balances:
            ID = account[0]
            balance = account[1]
            sql = "Update Accounts set Balance = {} where ID = {}".format(balance, ID)
            query = QSqlQuery(sql, self.db)

    def addEnvelope(self, category, subcategory):
        sql = "Insert into Envelopes \
        (category, subcategory) \
        values ('{}', '{}')".format(category, subcategory)
        query = QSqlQuery(sql, self.db)

    def addBudgetMonth(parent, month):
        sql = "Select * from Envelopes WHERE active=1"
        query = QSqlQuery(sql, parent.tempdb)
        envelopes = []
        while query.next():
            envelopes.append(query.value(0))
        print envelopes
        for envs in envelopes:
            sql = "Insert into Budget \
            (Month, subcategory, budgeted, actual) \
            VALUES ({},{},0,0)".format(month, envs)
            query = QSqlQuery(sql, parent.tempdb)

    def updateBudgetValues(date, subcategory, budgeted):
        pass

    def getAccounts(self):
        accounts = []
        sql = "Select Name, Balance from Accounts"
        query = QSqlQuery(sql, self.db)
        while query.next():
            accounts.append([query.value(0), query.value(1)])
        return accounts

    def getTransTable(self):
        self.parent.Tmodel = QSqlRelationalTableModel()
        self.parent.Tmodel.setTable("Transactions")
        self.parent.Tmodel.setRelation(7, QSqlRelation("Envelopes", "ID", "subcategory"))
        self.parent.Tmodel.setRelation(2, QSqlRelation("Accounts", "ID", "Name"))
        self.parent.Tmodel.setEditStrategy(QSqlTableModel.OnRowChange)
        if self.selectedAcc != 0:
            self.parent.Tmodel.setFilter("account={}".format(self.selectedAcc))
        self.parent.Tmodel.select()
        view = QTableView()
        view.setModel(self.parent.Tmodel)
        view.setItemDelegate(QSqlRelationalDelegate(view))
        view.setColumnHidden(0, True)
        return view
