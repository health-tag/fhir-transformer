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


def open_opx_csv(file_path: str) -> list[OdxCsvItem]:
    # hn|datedx|clinic|diag|dxtype|drdx|person_id|seq

    df = pd.read_csv(file_path, encoding="utf8", delimiter="|")
    df.columns = df.columns.str.upper()
    items = list[OdxCsvItem]()
    for i, row in df.iterrows():
        items.append(OdxCsvItem(sequence=row["SEQ"],
                                hospital_number=row["HN"],
                                visit_date=row["DATEDX"],
                                clinic_number=row["CLINIC"],
                                diagnosis_icd10=row["DIAG"],
                                diagnosis_type_number=row["DXTYPE"],
                                diagnosis_doctor=row["DRDX"],
                                citizen_id=row["PERSON_ID"]))
    return items