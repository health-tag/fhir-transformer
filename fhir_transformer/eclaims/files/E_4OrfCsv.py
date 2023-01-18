from dataclasses import dataclass
from os import PathLike

import pandas as pd

'''
hn       |dateopd X|clinic X|refer|refertype|seq
650069735|20220902 |        |10675|2        |065151491

dateopd clinic ไม่ใช้ เพราะใช้จาก 3 OPD ได้
'''


@dataclass
class OrfCsvRow:
    sequence: str = None
    hospital_number: str = None
    refer: str = None
    refer_type: str = None


def open_orf_csv(file_path: PathLike) -> list[OrfCsvRow]:
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|",dtype=str)
    df.columns = df.columns.str.lower()
    items = list[OrfCsvRow]()
    for i, row in df.iterrows():
        items.append(OrfCsvRow(sequence=row["seq"],
                               hospital_number=row["hn"],
                               refer=row["refer"],
                               refer_type=row["refertype"]))
    return items
