import sqlite3
import pandas as pd


def addAccountSQL(name, acctype, db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    sql = "Insert into Accounts values ('{}', 0, '{}')".format(name, acctype)
    c.execute(sql)
    conn.commit()
    conn.close()


def getTransSQL(account, db):
    conn = sqlite3.connect(db)
    sql = "Select * from Transactions where account LIKE '{}'".format(account)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


def insertTransSQL(df, db):
    conn = sqlite3.connect(db)
    df.to_sql("Transactions", conn, if_exists="append", index=False)
    conn.close()


def initTransTable(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''Create Table if not exists Transactions (Date text, account text, \
    payee text, memo text, cStatus integer, amount real, category text, flags text)''')
    conn.commit()
    conn.close()


def initAccTable(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''Create Table if not exists Accounts (Name text, Balance real, type text)''')
    conn.commit()
    conn.close()


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


def initEnvelopesTable(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''Create Table if not exists Envelopes (active integer, category text, \
    subcategory text)''')
    conn.commit()
    conn.close()
    initevelopes = [
        ["Expenses", "Housing"],
        ["Expenses", "Groceries"],
        ["Expenses", "Utilities"],
        ["Savings", "Holidays"],
        ["Savings", "EmergencyFund"],
        ["Savings", "ShinyThing"]
    ]
    for envs in initevelopes:
        addEnvelope(db, envs[0], envs[1])


def initBudgetTable(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''Create Table if not exists Budget (date text, subcategory text, \
    budgeted real)''')
    conn.commit()
    conn.close()


def addEnvelope(db, category, subcategory):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    sql = "Insert into Envelopes values (1, '{}', '{}')".format(category, subcategory)
    c.execute(sql)
    conn.commit()
    conn.close()


def editBudget(date, subcategory, budgeted):
    pass
