import sqlite3
import pandas as pd
from QIF_Handler import *
from PySide.QtSql import *


def addAccountSQL(name, acctype, parent):
    sql = "Insert into Accounts values ('{}', 0, '{}')".format(name, acctype)
    query = QSqlQuery(sql, parent.tempdb)


def insertTransSQL(filename, parent): # update
    df = readQif(filename, parent.selectedAcc)
    colList= list(df.columns.values)
    sql = "Insert into Transactions ({}) values ({})"
    headers = ", ".join([i for i in colList])
    blanks = ", ".join(["?" for i in colList])
    sql = sql.format(headers, blanks)
    query = QSqlQuery(parent.tempdb)
    query.prepare(sql)
    for cols in colList:
        query.addBindValue(df[cols].tolist())
    query.execBatch()
    # conn = sqlite3.connect(db)
    # conn.text_factory = str
    # df.to_sql("Transactions", conn, if_exists="append", index=False)
    # conn.close()


def initNewDB(parent):
    sql = '''Create Table if not exists Transactions (Date text, account text, \
    payee text, memo text, cStatus integer, amount real, category text, flags text)'''
    query = QSqlQuery(sql, parent.tempdb)
    sql = '''Create Table if not exists Accounts (Name text, Balance real, type text)'''
    query = QSqlQuery(sql, parent.tempdb)
    sql = '''Create Table if not exists Envelopes (active integer, category text, \
    subcategory text)'''
    query = QSqlQuery(sql, parent.tempdb)
    initevelopes = [
        ["Expenses", "Housing"],
        ["Expenses", "Groceries"],
        ["Expenses", "Utilities"],
        ["Savings", "Holidays"],
        ["Savings", "EmergencyFund"],
        ["Savings", "ShinyThing"]
    ]
    for envs in initevelopes:
        addEnvelope(parent, envs[0], envs[1])
    sql='''Create Table if not exists Budget (date text, subcategory text, \
    budgeted real)'''
    query = QSqlQuery(sql, parent.tempdb)


def updateAccSQLBalance(parent):
    sql = "Select Name from Accounts"
    query = QSqlQuery(sql, parent.tempdb)
    accounts = []
    while query.next(): accounts.append(query.value(0))
    balances = []
    for account in accounts:
        sql = "Select Sum(amount) from Transactions where account='{}'".format(account)
        query = QSqlQuery(sql, parent.tempdb)
        query.next()
        if query.value(0) != "":
            balance = round(query.value(0), 2)
            balances.append([account, balance])
    for account in balances:
        name = account[0]
        balance = account[1]
        sql = "Update Accounts set Balance = {} where Name = '{}'".format(balance, name)
        query = QSqlQuery(sql, parent.tempdb)


def addEnvelope(parent, category, subcategory):
    sql = "Insert into Envelopes values (1, '{}', '{}')".format(category, subcategory)
    query = QSqlQuery(sql, parent.tempdb)


def editBudget(date, subcategory, budgeted):
    pass


def getAccounts(parent):
    accounts = []
    sql = "Select Name, Balance from Accounts"
    query = QSqlQuery(sql, parent.tempdb)
    while query.next():
        accounts.append([query.value(0),query.value(1)])
    return accounts
