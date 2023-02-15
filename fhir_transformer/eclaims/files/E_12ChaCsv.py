from dataclasses import dataclass
from os import PathLike

import pandas as pd

"""
hn       |an|date    |chrgitem |amount|person_id    |seq
658574908|  |20220915|31       |645.00|9253080438132|065158037
"""


@dataclass
class ChaCsvRow:
    hospital_number: str
    citizen_id: str
    date: str
    chrgitem: str
    amount: str
    sequence: str


def open_cha_csv(file_path: PathLike) -> list[ChaCsvRow]:
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|", dtype=str)
    df.columns = df.columns.str.lower()
    items = list[ChaCsvRow]()
    for i, row in df.iterrows():
        items.append(ChaCsvRow(sequence=row["seq"],
                               hospital_number=row["hn"],
                               citizen_id=row["person_id"],
                               date=row["date"],
                               chrgitem=row["chrgitem"],
                               amount=row["amount"]))
    return items
