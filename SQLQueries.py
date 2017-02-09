initTransactions = '''Create Table if not exists Transactions (
    ID integer PRIMARY KEY,
    TransDate DATE,
    account integer,
    payee text,
    memo text,
    cStatus integer,
    amount real,
    category integer DEFAULT 1,
    flags text
    )'''

initAccounts = '''Create Table if not exists Accounts (
    ID integer PRIMARY KEY,
    Name text UNIQUE,
    Balance real,
    type text
    )'''

initBudget = '''Create Table if not exists Budget (
    ID integer PRIMARY KEY,
    theMonth Date,
    subCategory integer,
    budgeted real default 0,
    actual real default 0,
    balance real default 0,
    UNIQUE(theMonth, subCategory)
    )'''

initEnvelopes = '''Create Table if not exists Envelopes (
    ID integer PRIMARY KEY,
    category text,
    subcategory text
    )'''

initBudTrigIns = '''Create Trigger budget_balance_ins
    after Insert
    ON Budget
    BEGIN
        Update budget set balance = budgeted+actual;
    END;
    '''

initBudTrigUpd = '''Create Trigger budget_balance_upd
    after Update
    ON Budget
    BEGIN
        Update budget set balance = budgeted+actual;
    END;
    '''

initDelCatTrig = '''Create Trigger delete_category
    after delete
    on Envelopes
    BEGIN
        update Transactions set category = 1 where category = OLD.ID;
        delete from Budget where subCategory = OLD.ID;
    END;
    '''

initList = [initTransactions, initAccounts,
            initBudget, initEnvelopes,
            initBudTrigIns, initBudTrigUpd,
            initDelCatTrig]

updateBudgetValues = ['''Insert OR IGNORE into Budget
    (theMonth, subCategory,actual)
    Select strftime('%Y-%m', TransDate) AS Mo,
        category as cat,
        sum(amount) as tot
    from Transactions
    group by strftime('%Y-%m', TransDate), category;''',

    '''REPLACE into Budget
    (theMonth, subCategory, budgeted, actual)
        Select a.theMonth, a.cat, b.budgeted, a.tot
        from
            (Select
                strftime('%Y-%m', TransDate) as theMonth,
                category as cat,
                sum(amount) as tot
            FROM Transactions
            group by strftime('%Y-%m', TransDate), category)
            as a
        INNER JOIN Budget
        as b
        ON a.theMonth=b.theMonth AND a.cat=b.subCategory;
    ''']
