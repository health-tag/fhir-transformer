from dataclasses import dataclass

import pandas as pd

'''
hn|clinic|dateopd|timeopd|seq|uuc
653586040|0121|20220901|0925|065150995|1
'''

@dataclass
class OpdCsvRow:
    sequence: str = None
    """ SEQ """
    hospital_number: str = None
    """ HN """
    clinic_number: str = None
    """ CLINIC """
    visit_date: str = None
    """ DATEOPD """
    visit_time: str = None
    """ TIMEOPD """



def open_opd_csv(file_path: str) -> list[OpdCsvRow]:
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|")
    df.columns = df.columns.str.lower()
    items = list[OpdCsvRow]()
    for i, row in df.iterrows():
        items.append(OpdCsvRow(sequence=row["seq"],
                               hospital_number=row["hn"],
                               clinic_number=row["clinic"],
                               visit_date=row["dateopd"],
                               visit_time=row["timeopd"]))
    return items
