import pandas as pd


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
