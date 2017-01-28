import sqlite3
import pandas as pd
from PySide.QtSql import *


def addAccountSQL(name, acctype, parent):
    sql = "Insert into Accounts values ('{}', 0, '{}')".format(name, acctype)
    query = QSqlQuery(sql, parent.tempdb)


def insertTransSQL(df, db):
    conn = sqlite3.connect(db)
    conn.text_factory = str
    df.to_sql("Transactions", conn, if_exists="append", index=False)
    conn.close()


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


def updateAccSQLBalance(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    sql = "Select Name from Accounts"
    df = pd.read_sql_query(sql, conn)
    accounts = list(df["Name"])
    balances = []
    for account in accounts:
        sql = "Select Sum(amount) from Transactions where account='{}'".format(account)
        c.execute(sql)
        balance = round(c.fetchone()[0], 2)
        balances.append([account, balance])
    for account in balances:
        name = account[0]
        balance = account[1]
        sql = "Update Accounts set Balance = {} where Name = '{}'".format(balance, name)
        c.execute(sql)
    conn.commit()
    conn.close()


def addEnvelope(parent, category, subcategory):
    sql = "Insert into Envelopes values (1, '{}', '{}')".format(category, subcategory)
    query = QSqlQuery(sql, parent.tempdb)


def editBudget(date, subcategory, budgeted):
    pass


def getAccounts(db):
    accounts = []
    conn = sqlite3.connect(db)
    c = conn.cursor()
    sql = "Select * from Accounts"
    c.execute(sql)
    acc = c
    for ac in acc:
        accounts.append(ac)
    return accounts
