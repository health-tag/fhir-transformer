from dataclasses import dataclass
from os import PathLike

import pandas as pd

"""
hn       |an|date    |total |paid|pttype|person_id    |seq
651218347|  |20220912|532.50|0.00|77    |1842228343492|065156262
"""

@dataclass
class ChtCsvRow:
    hospital_number: str
    citizen_id: str
    date: str
    patient_type:str
    sequence:str

def open_cht_csv(file_path: PathLike) -> list[ChtCsvRow]:
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|")
    df.columns = df.columns.str.lower()
    items = list[ChtCsvRow]()
    for i, row in df.iterrows():
        items.append(ChtCsvRow(sequence=row["seq"],
                               hospital_number=row["hn"],
                               citizen_id=row["person_id"],
                               date=row["date"],
                               patient_type=row["pttype"]))
    return items