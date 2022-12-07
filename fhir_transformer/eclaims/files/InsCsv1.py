from dataclasses import dataclass
from os import PathLike

import pandas as pd


@dataclass
class InsCsvItem:
    hospital_number: str
    citizen_id: str
    insurance: str
    sequence: str
    main_hospital_code:str

#hn       |inscl|subtype|cid          |datein  |dateexp|hospmain|hospsub|govcode|govname|permitno|docno|ownrpid|ownname|an|seq      |subinscl|relinscl|htype
#651218347|UCS  |77     |1842228343492|20180728|       |11218   |07043  |       |       |        |     |       |       |  |065156262|null    |null    |

"""
UCS = สิทธิ UC
OFC = ข้าราชการ
SSS = ประกันสังคม
LGO = อปท
SSI = ประกันสังคมทุพพลภาพ
"""
def open_ins_csv(file_path: PathLike) -> list[InsCsvItem]:
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|")
    df.columns = df.columns.str.lower()
    items = list[InsCsvItem]()
    for i, row in df.iterrows():
        items.append(InsCsvItem(sequence=row["seq"],
                                hospital_number=row["hn"],
                                citizen_id=row["cid"],
                                insurance=row["inscl"],
                                main_hospital_code=row["hospmain"]))
    return items
