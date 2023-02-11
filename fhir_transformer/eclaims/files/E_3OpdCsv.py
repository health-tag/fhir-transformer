from dataclasses import dataclass
from os import PathLike

import pandas as pd

'''
hn|clinic|dateopd|timeopd|seq|uuc
653586040|0121|20220901|0925|065150995|1
'''

@dataclass
class OpdCsvRow:
    sequence: str = None
    hospital_number: str = None
    optype: str = None
    clinic: str = None
    dateopd: str = None
    timeopd: str = None
    uuc: str = None



def open_opd_csv(file_path: PathLike) -> list[OpdCsvRow]:
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|",dtype=str)
    df.columns = df.columns.str.lower()
    items = list[OpdCsvRow]()
    for i, row in df.iterrows():
        items.append(OpdCsvRow(sequence=row["seq"],
                               hospital_number=row["hn"],
                               clinic=row["clinic"],
                               optype=5,
                               dateopd=row["dateopd"],
                               timeopd=row["timeopd"],
                               uuc=row["uuc"]))
    return items
