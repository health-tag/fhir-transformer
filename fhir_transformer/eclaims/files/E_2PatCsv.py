from dataclasses import dataclass
from os import PathLike

import pandas as pd


@dataclass
class PatCsvRow:
    hospital_code:str
    title: str
    name: str
    surname: str
    gender_number: str
    martial_status_number: str
    citizen_id: str
    hospital_number: str
    nationality_code: str
    occupational_code: str
"""
hcode|hn       |changwat|amphur|dob     |sex|marriage|occupa|nation|person_id    |namepat                          |title|fname       |lname           |idtype
11218|651218347|60      |11    |19580101|1  |2       |505   |099   |1842228343492|ตัวอย่างชื่อ-6138 ตัวอย่างนามสกุล-4970,นาย|นาย  |ตัวอย่างชื่อ-6138|ตัวอย่างนามสกุล-4970|1
"""
def open_pat_csv(file_path: PathLike) -> list[PatCsvRow]:
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|")
    df.columns = df.columns.str.lower()
    items = list[PatCsvRow]()
    for i, row in df.iterrows():
        items.append(PatCsvRow(hospital_code=row["hcode"],
                               title=row["title"],
                               name=row["fname"],
                               surname=row["lname"],
                               gender_number=row["sex"],
                               martial_status_number=row["marriage"],
                               citizen_id=row["person_id"],
                               hospital_number=row["hn"],
                               nationality_code=row["nation"],
                               occupational_code=row["occupa"]))
    return items