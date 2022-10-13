import pandas as pd

from fhir_transformer.eclaims.entity.PatCsv import PatCsvItem


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
                                citizenId=row["person_id"],
                                hospital_number=row["hn"],
                                nationality_code=row["nation"],
                                occupational_code=row["occupa"]))
    return items
