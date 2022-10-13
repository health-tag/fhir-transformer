from dataclasses import dataclass

@dataclass
class PatCsvItem:
    hospital_code:str
    title: str
    name: str
    surname: str
    gender_number: str
    martial_status_number: str
    citizenId: str
    hospital_number: str
    nationality_code: str
    occupational_code: str
