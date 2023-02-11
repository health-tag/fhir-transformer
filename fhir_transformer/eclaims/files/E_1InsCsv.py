from dataclasses import dataclass
from os import PathLike

import pandas as pd

"""
hn       |inscl|subtype|cid          |datein  |dateexp|hospmain|hospsub|govcode|govname|permitno|docno|ownrpid|ownname|an|seq      |subinscl|relinscl|htype
651218347|UCS  |77     |1842228343492|20180728|       |11218   |07043  |       |       |        |     |       |       |  |065156262|null    |null    |
"""
@dataclass
class InsCsvRow:
    htype: str
    hospital_number: str
    citizen_id: str
    insurance_type: str
    insurance_expired_date: str
    subtype: str
    main_hospital_code:str
    primary_care_hospital_code:str
    sequence: str

"""
UCS = สิทธิ UC
OFC = ข้าราชการ
SSS = ประกันสังคม
LGO = อปท
SSI = ประกันสังคมทุพพลภาพ
"""
def open_ins_csv(file_path: PathLike) -> list[InsCsvRow]:
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|",dtype=str)
    df.columns = df.columns.str.lower()
    items = list[InsCsvRow]()
    for i, row in df.iterrows():
        items.append(InsCsvRow(sequence=row["seq"],
                               htype=row["htype"],
                               hospital_number=row["hn"],
                               citizen_id=row["cid"],
                               insurance_type=row["inscl"],
                               insurance_expired_date=row["dateexp"],
                               subtype=row["subtype"],
                               main_hospital_code=row["hospmain"],
                               primary_care_hospital_code=row["hospsub"]))
    return items
