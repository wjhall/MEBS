import sqlite3
import pandas as pd
import sys
from PySide.QtCore import *
from PySide.QtGui import *


class MEBS(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        menu = getMenuBar()
        self.setMenuBar(menu)

        self.main = QWidget(self)
        self.TransData = getTransSQL('123Std')
        self.TransTable = dfToQTab(self.TransData)

        self.AccBox = QGroupBox("Accounts", self.main)
        self.AccBox.setLayout(AccountsListVBox())

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.AccBox)
        self.layout.addWidget(self.TransTable)
        self.main.setLayout(self.layout)

        self.setCentralWidget(self.main)
        self.show()


def getMenuBar():
    menu = QMenuBar()
    menu.addMenu("File")
    return menu


def dfToQTab(df):
    datatable = QTableWidget()
    datatable.setColumnCount(len(df.columns))
    datatable.setRowCount(len(df.index))
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            datatable.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
    datatable.setHorizontalHeaderLabels(df.columns)
    return datatable


def initTransTable():
    conn = sqlite3.connect("C:/Users/whall/Documents/dev/MEBS/python/mydb.db")
    c = conn.cursor()
    c.execute('''Create Table if not exists Transactions (Date text, account text, \
    payee text, memo text, cStatus integer, amount real, category text, flags text)''')
    conn.commit()
    conn.close()


def initAccTable():
    conn = sqlite3.connect("C:/Users/whall/Documents/dev/MEBS/python/mydb.db")
    c = conn.cursor()
    c.execute('''Create Table if not exists Accounts (Name text, Balance real)''')
    conn.commit()
    conn.close()


def AccountsListVBox():
    vbox = QVBoxLayout()
    conn = sqlite3.connect("C:/Users/whall/Documents/dev/MEBS/python/mydb.db")
    c = conn.cursor()
    sql = "Select * from Accounts"
    c.execute(sql)
    accounts = c
    for account in accounts:
        button = QPushButton(account[0])
        label = QLabel(str(account[1]))
        vbox.addWidget(button)
        vbox.addWidget(label)
    return vbox


def updateAccSQLBalance():
    conn = sqlite3.connect("C:/Users/whall/Documents/dev/MEBS/python/mydb.db")
    c = conn.cursor()
    sql = "Select Distinct Name from Accounts"
    c.execute(sql)
    accounts = c
    balances = []
    for account in accounts:
        name = account[0]
        sql = "Select Sum(amount) from Transactions where account='{}'".format(name)
        c.execute(sql)
        balance = round(c.fetchone()[0], 2)
        balances.append([name, balance])
    for account in balances:
        name = account[0]
        balance = account[1]
        sql = "Update Accounts set Balance = {} where Name = '{}'".format(balance, name)
        c.execute(sql)
    conn.commit()
    conn.close()


def addAccountSQL(name):
    conn = sqlite3.connect("C:/Users/whall/Documents/dev/MEBS/python/mydb.db")
    c = conn.cursor()
    sql = "Insert into Accounts values ('{}', 0)".format(name)
    c.execute(sql)
    conn.commit()
    conn.close()


def parseQifLine(line):
    code = {
        "D": "Date",
        "T": "amount",
        "P": "Payee"
    }.get(line[0], "None")
    if code == "Amount":
        value = float(line[1:])
    else:
        value = line[1:]
    return {code: value}


def readQif(filename, account):
    with open(filename) as f:
        transactions = f.read().split("\n^\n")
        df = pd.DataFrame()
        for transaction in transactions:
            transdict = {}
            for line in transaction.split("\n"):
                transdict.update(parseQifLine(line))
            df = df.append(transdict, ignore_index=True)
    df["account"] = account
    df.drop(("None"), axis=1, inplace=True)
    return df


def getTransSQL(account):
    conn = sqlite3.connect("C:/Users/whall/Documents/dev/MEBS/python/mydb.db")
    sql = "Select * from Transactions where account='{}'".format(account)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


def insertTransSQL(df):
    conn = sqlite3.connect("C:/Users/whall/Documents/dev/MEBS/python/mydb.db")
    df.to_sql("Transactions", conn, if_exists="append", index=False)
    conn.close()
    return

filename = "C:/Users/whall/Documents/dev/MEBS/python/example.qif"

# initTransTable()
# initAccTable()

# addAccountSQL("123Std")
# TransData = readQif(filename, '123Std')
# insertTransSQL(TransData)
# updateAccSQLBalance()

app = QApplication(sys.argv)
UI = MEBS()
app.exec_()
sys.exit()
