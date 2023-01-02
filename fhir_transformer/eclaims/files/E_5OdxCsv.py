from dataclasses import dataclass
from os import PathLike

import pandas as pd

'''
hn|datedx|clinic|diag|dxtype|drdx|person_id|seq

'''


@dataclass
class OdxCsvRow:
    sequence:str
    hospital_number:str
    visit_date:str
    clinic_number:str
    diagnosis_icd10:str
    diagnosis_type_number:str
    diagnosis_doctor:str
    citizen_id:str


def open_odx_csv(file_path: PathLike) -> list[OdxCsvRow]:

    df = pd.read_csv(file_path, encoding="utf8", delimiter="|")
    df.columns = df.columns.str.lower()
    items = list[OdxCsvRow]()
    for i, row in df.iterrows():
        items.append(OdxCsvRow(sequence=row["seq"],
                               hospital_number=row["hn"],
                               visit_date=row["datedx"],
                               clinic_number=row["clinic"],
                               diagnosis_icd10=row["diag"],
                               diagnosis_type_number=row["dxtype"],
                               diagnosis_doctor=row["drdx"],
                               citizen_id=row["person_id"]))
    return items