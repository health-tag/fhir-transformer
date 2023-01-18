from dataclasses import dataclass
from os import PathLike

import pandas as pd


@dataclass
class DruCsvRow:
    hospital_code: str
    """hcode"""
    hospital_number: str
    """hn"""
    admission_number: str
    """an"""
    clinic_number: str
    """clinic"""
    person_id: str
    """person_id"""
    service_date: str
    """date_serv"""
    drug_id: str
    """did"""
    drug_name: str
    """didname"""
    amount: str
    """amount"""
    drug_id24: str
    """didstd"""
    unit: str
    """unit"""
    unit_pack: str
    """unit_pack"""
    sequence: str
    """seq"""
    use_status: str
    """use_status
    1 = ใช้ในโรงพยาบาล
    2 = ใช้ที่บ้าน
    """
    """
    01 MEDICINE (อายุรกรรม)
    02 SURGERY (ศัลยกรรม)
    03 OB (สูติกรรม)
    04 GYN (นรีเวชกรรม)
    05 PED (กุมารเวช)
    06 ENT (โสต ศอ นาสิก)
    07 EYE (จักษุ)
    08 ORTHOPEDICS (ศัลยกรรมกระดูก)
    09 PSYCHIATRY (จิตเวช)
    10 RADIOLOGY (รังสีวิทยา)
    11 DENTAL (ทันตกรรม)
    12 OTHER (อื่นๆ
    """
#hcode|hn|an|clinic|person_id|date_serv|did|didname|amount|drugpric|drugcost|didstd|unit|unit_pack|seq|drugremark|pa_no|totcopay|use_status|total
#11218|651218347||0011|1842228343492|20220912|D0000910|Guaifenesin 200 mg tab|20.00|1.0|0.24|101124000014203120381144|เม็ด||065156262|||0.00|2|20.00

def open_dru_csv(file_path: PathLike) -> list[DruCsvRow]:
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|",dtype=str)
    df.columns = df.columns.str.lower()
    items = list[DruCsvRow]()
    for i, row in df.iterrows():
        items.append(DruCsvRow(hospital_code=row["hcode"],
                               hospital_number=row["hn"],
                               admission_number=row["an"],
                               clinic_number=row["clinic"],
                               person_id=row["person_id"],
                               service_date=row["date_serv"],
                               drug_id=row["did"],
                               drug_name=row["didname"],
                               amount=row["amount"],
                               drug_id24=row["didstd"],
                               unit=row["unit"],
                               unit_pack=row["unit_pack"],
                               sequence=row["seq"],
                               use_status=row["use_status"],
                               ))
    return items
