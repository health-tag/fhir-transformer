from dataclasses import dataclass


@dataclass
class OdxCsvItem:
    sequence:str
    """SEQ"""
    hospital_number:str
    """HN"""
    visit_date:str
    """DATEDX"""
    clinic_number:str
    """CLINIC"""
    diagnosis_icd10:str
    """DIAG"""
    diagnosis_type_number:str
    """DXTYPE"""
    diagnosis_doctor:str
    """DRDX"""
    citizen_id:str
    """PERSON_ID"""

    #hn|datedx|clinic|diag|dxtype|drdx|person_id|seq