import sqlite3
import pandas as pd
from QIF_Handler import *
from PySide.QtSql import *


def accountID(parent, name):
    sql = "SELECT ID from accounts WHERE Name='{}'".format(name)
    query = QSqlQuery(sql, parent.tempdb)
    query.first()
    return query.value(0)


def addAccountSQL(name, acctype, parent):
    sql = "Insert into Accounts (Name, Balance, Type) values ('{}', 0, '{}')".format(name, acctype)
    query = QSqlQuery(sql, parent.tempdb)


def insertTransSQL(filename, parent):
    with QIF_Handler() as QIF:
        df = QIF.readQif(filename, parent.selectedAcc)
    colList = list(df.columns.values)
    sql = "Insert into Transactions ({}) values ({})"
    headers = ", ".join([i for i in colList])
    blanks = ", ".join(["?" for i in colList])
    sql = sql.format(headers, blanks)
    parent.tempdb.transaction()
    query = QSqlQuery(parent.tempdb)
    query.prepare(sql)
    for cols in colList:
        query.addBindValue(df[cols].tolist())
    query.execBatch()
    parent.tempdb.commit()


def initNewDB(parent):
    sql = '''Create Table if not exists Envelopes (\
        ID integer PRIMARY KEY, \
        category text, \
        subcategory text)'''
    query = QSqlQuery(sql, parent.tempdb)
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
        addEnvelope(parent, envs[0], envs[1])
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
    query = QSqlQuery(sql, parent.tempdb)
    sql = '''Create Table if not exists Accounts (\
        ID integer PRIMARY KEY, \
        Name text UNIQUE, \
        Balance real, \
        type text)'''
    query = QSqlQuery(sql, parent.tempdb)
    sql = '''Create Table if not exists Budget (\
        ID integer PRIMARY KEY, \
        Month Date, \
        subcategory integer, \
        budgeted real, \
        actual real)'''
    query = QSqlQuery(sql, parent.tempdb)


def updateAccSQLBalance(parent):
    sql = "Select ID from Accounts"
    query = QSqlQuery(sql, parent.tempdb)
    accounts = []
    while query.next():
        accounts.append(query.value(0))
    balances = []
    for account in accounts:
        sql = "Select Sum(amount) from Transactions where account={}".format(account)
        query = QSqlQuery(sql, parent.tempdb)
        query.next()
        if query.value(0) != "":
            balance = round(query.value(0), 2)
            balances.append([account, balance])
    for account in balances:
        ID = account[0]
        balance = account[1]
        sql = "Update Accounts set Balance = {} where ID = {}".format(balance, ID)
        query = QSqlQuery(sql, parent.tempdb)


def addEnvelope(parent, category, subcategory):
    sql = "Insert into Envelopes \
    (category, subcategory) \
    values ('{}', '{}')".format(category, subcategory)
    query = QSqlQuery(sql, parent.tempdb)


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


def getAccounts(parent):
    accounts = []
    sql = "Select Name, Balance from Accounts"
    query = QSqlQuery(sql, parent.tempdb)
    while query.next():
        accounts.append([query.value(0), query.value(1)])
    return accounts
