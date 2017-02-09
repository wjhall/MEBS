initTransactions = '''Create Table if not exists Transactions (\
    ID integer PRIMARY KEY, \
    TransDate DATE, \
    account integer, \
    payee text, \
    memo text, \
    cStatus integer, \
    amount real, \
    category integer DEFAULT 1, \
    flags text \
    )'''

initAccounts = '''Create Table if not exists Accounts (\
    ID integer PRIMARY KEY, \
    Name text UNIQUE, \
    Balance real, \
    type text \
    )'''

initBudget = '''Create Table if not exists Budget (\
    ID integer PRIMARY KEY, \
    theMonth Date, \
    subCategory integer, \
    budgeted real, \
    actual real,
    UNIQUE(theMonth, subCategory) \
    )'''

initEnvelopes = '''Create Table if not exists Envelopes (\
    ID integer PRIMARY KEY, \
    category text, \
    subcategory text \
    )'''

initList = [initTransactions, initAccounts, initBudget, initEnvelopes]

updateBudgetValues = ['''Insert OR IGNORE into Budget
    (theMonth, subCategory,actual)
    Select strftime('%Y-%m', TransDate) AS Mo,
        category as cat,
        sum(amount) as tot
    from Transactions
    group by strftime('%Y-%m', TransDate), category;''',

    '''REPLACE into Budget
    (theMonth,subCategory, budgeted, actual)
        (Select a.theMonth, a.cat, b.budgeted, a.tot
        from
            (Select
                strftime('%Y-%m', TransDate) as theMonth,
                category as cat,
                sum(amount) as tot
            FROM Transactions
            group by strftime('%Y-%m', TransDate), category)
            as a)
        INNER JOIN Budget
        as b
        ON a.theMonth=b.theMonth AND a.cat=b.subCategory;)
    )''']
