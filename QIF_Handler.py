import pandas as pd
import datetime as dt
from PySide.QtSql import *


class QIF_Handler():
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def parseQifLine(self, line):
        code = {
            "D": "TransDate",
            "T": "amount",
            "P": "Payee"
        }.get(line[0], "None")
        if code == "TransDate":
            value = dt.datetime.strftime(dt.datetime.strptime(line[1:], "%d/%m/%Y"), "%Y-%m-%d")
        elif code == "Amount":
            value = float(line[1:])
        else:
            value = line[1:]
        return {code: value}

    def readQif(self, filename, account):
        with open(filename) as f:
            transactions = f.read().split("\n^\n")
            df = pd.DataFrame()
            for transaction in transactions:
                transdict = {}
                for line in transaction.split("\n"):
                    transdict.update(self.parseQifLine(line))
                df = df.append(transdict, ignore_index=True)
        df["account"] = account
        df["category"] = 1
        df.drop(("None"), axis=1, inplace=True)
        return df
