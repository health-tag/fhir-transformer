from dataclasses import dataclass


@dataclass
class DruCsvItem:
    hospital_code: str
    """HCODE"""
    hospital_number: str
    """HN"""
    admission_number: str
    """AN"""
    clinic_number: str
    """CLINIC"""
    person_id: str
    """PERSON_ID"""
    service_date: str
    """DATE_SERVE"""
    drug_id: str
    """DID"""
    drug_name: str
    """DIDNAME"""
    amount: str
    """AMOUNT"""
    drug_id24: str
    """DIDSTD"""
    unit: str
    """UNIT"""
    unit_pack: str
    """UNIT_PACK"""
    sequence: str
    """SEQ"""
    use_status: str
    """USE_STATUS
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
    # hcode|hn|an|clinic|person_id|date_serv|did|didname|amount|drugpric|drugcost|didstd|unit|unit_pack|seq|drugremark|pa_no|totcopay|use_status|total