from dataclasses import dataclass


@dataclass
class PersonCsvItem:
    citizen_id: str
    internal_pid: str
    hospital_number: str
    name: str
    surname: str
    gender_number: str
    martial_status_number: str
    hospital_code: str
    nationality_code: str
    occupational_code: str


@dataclass
class PersonCSV:
    hospital_code: str
    items_dict: dict[str, PersonCsvItem]
