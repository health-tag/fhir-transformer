import pandas as pd

from fhir_transformer.eclaims.entity.DruCsv16 import DruCsvItem
from fhir_transformer.eclaims.entity.InsCsv1 import InsCsvItem
from fhir_transformer.eclaims.entity.OdxCsv5 import OdxCsvItem
from fhir_transformer.eclaims.entity.OpdCsv3 import OpdCsvItem
from fhir_transformer.eclaims.entity.PatCsv2 import PatCsvItem


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


def open_opd_csv(file_path: str) -> list[OpdCsvItem]:
    pass


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


def open_ins_csv(file_path: str) -> list[InsCsvItem]:
    # hn|inscl|subtype|cid|datein|dateexp|hospmain|hospsub|govcode|govname|permitno|docno|ownrpid|ownname|an|seq|subinscl|relinscl|htype
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|")
    df.columns = df.columns.str.upper()
    items = list[InsCsvItem]()
    for i, row in df.iterrows():
        items.append(InsCsvItem(sequence=row["SEQ"],
                                hospital_number=row["HN"],
                                citizen_id=row["DATEDX"],
                                insurance=row["CLINIC"]))
    return items


def open_dru_csv(file_path: str) -> list[DruCsvItem]:
    # hcode|hn|an|clinic|person_id|date_serv|did|didname|amount|drugpric|drugcost|didstd|unit|unit_pack|seq|drugremark|pa_no|totcopay|use_status|total
    df = pd.read_csv(file_path, encoding="utf8", delimiter="|")
    df.columns = df.columns.str.upper()
    items = list[DruCsvItem]()
    for i, row in df.iterrows():
        items.append(DruCsvItem(hospital_code=row["HCODE"],
                                hospital_number=row["HN"],
                                admission_number=row["AN"],
                                clinic_number=row["CLINIC"],
                                person_id=row["PERSON_ID"],
                                service_date=row["DATE_SERVE"],
                                drug_id=row["DID"],
                                drug_name=row["DIDNAME"],
                                amount=row["AMOUNT"],
                                drug_id24=row["DIDSTD"],
                                unit=row["UNIT"],
                                unit_pack=row["UNIT_PACK"],
                                sequence=row["SEQ"],
                                use_status=row["USE_STATUS"],
                                ))
    return items
