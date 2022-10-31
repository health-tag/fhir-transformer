from dataclasses import dataclass

import pandas as pd


@dataclass
class PatCsvItem:
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


def open_pat_csv(file_path: str) -> list[PatCsvItem]:
    # hcode|hn|changwat|amphur|dob|sex|marriage|occupa|nation|person_id|namepat|title|fname|lname|idtype
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|")
    df.columns = df.columns.str.lower()
    items = list[PatCsvItem]()
    for i, row in df.iterrows():
        items.append(PatCsvItem(hospital_code=row["hcode"],
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