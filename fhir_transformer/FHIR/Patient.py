from enum import Enum

from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Entry import Entry
from fhir_transformer.FHIR.Organization import Organization
from fhir_transformer.FHIR.supports.support import Identifier, Coding, Builder
from fhir_transformer.csop.files.billtrans import BillTransItem
from fhir_transformer.eclaims.files.E_2PatCsv import PatCsvRow
from fhir_transformer.folders43.files.PersonCsv import PersonCsvItem


class Gender(Enum):
    Male = 1
    Female = 2

    def __getstate__(self):
        match self.value:
            case 1:
                return "male"
            case 2:
                return "female"


class MaritalStatus(Enum):
    # Value อ้างตาม 17 และ 43 แฟ้ม
    Single = 1  # โสด
    Married = 2  # สมรส
    Widow = 3  # หม้าย

    def __getstate__(self):
        match self.value:
            case 1:
                return "S"
            case 2:
                return "M"
            case 3:
                return "W"


patient_HN_identifier_system = "https://sil-th.org/fhir/Id/hn"


# "https://sil-th.org/CSOP/hn"


class Patient(FHIRResource):
    def __getstate__(self):
        return super().__getstate__()

    def __init__(self):
        super().__init__(resource_type="Patient")
        self._name: str | None = None
        self._surname: str | None = None
        self.gender: Gender | None = None
        self._maritalStatus: MaritalStatus | None = None
        self._combine_name_surname: str | None = None
        self._personal_id: str | None = None
        self._hospital_number: str | None = None
        self._nationality_code: str | None = None
        self._occupational_code: str | None = None
        self.generalPractitioner = list[dict[str, str | dict[str, str]]]()
        self._managingOrganizationURL: str | None = None
        # CSOP Only
        self._member_number: str | None = None

    def create_entry(self) -> Entry:
        # Note: urn:uuid: is only working in transaction only. It's better to use full URL instead
        # Old urn urn:uuid:Patient/{self._hospital_code}/{self._hospital_number}
        entry = Entry(self.get_resource_id_url(), self, {
            "method": "PUT",
            "url": self.get_resource_id_url(),
            "ifNoneExist": self.id #f"identifier={self.identifier[0].get_string_for_reference()}"
        })
        return entry

    def get_resource_url(self) -> str:
        return f"{self.resourceType}?identifier={self.identifier[0].get_string_for_reference()}"

    def get_resource_id_url(self) -> str:
        return f"{self.resourceType}/{self.id}"

    @property
    def name(self) -> list[dict[str, str | dict[str, str]]]:
        if (self._combine_name_surname is not None) and (self._combine_name_surname.strip() != ""):
            name_json = [
                {
                    "use": "official",
                    "text": f"{self._combine_name_surname}",
                }
            ]
        else:
            name_json = {
                "use": "official",
                "text": f"{self._name} {self._surname}",
                "family": self._surname,
                "given": [
                    self._name
                ]
            }
        return [name_json]

    @property
    def identifier(self):
        # Ref: https://terms.sil-th.org/identifier-systems.html
        identity_list = [
            Identifier("https://www.dopa.go.th", f"{self._personal_id}"),
            Identifier("https://terms.sil-th.org/id/th-cid", f"{self._personal_id}"),
            Identifier("https://sil-th.org/CSOP/hn", f"{self._hospital_number}"),
            Identifier(patient_HN_identifier_system, f"{self._hospital_number}"),
        ]
        if (self._member_number is not None) and (self._member_number.strip() != ""):
            identity_list.append(Identifier("https://sil-th.org/CSOP/memberNo", f"{self._member_number}"))
        return identity_list

    @property
    def id(self):
        return f"TH-CID-{self._personal_id}"
    @property
    def extension(self):
        if self._nationality_code is None or self._occupational_code is None:
            return None
        extensions = list()
        if self._nationality_code is not None:
            extensions.append({
                "url": "http://hl7.org/fhir/StructureDefinition/patient-nationality",
                "extension": [
                    {
                        "url": "code",
                        "valueCodeableConcept": {
                            "coding": [
                                Coding("https://sil-th.org/fhir/CodeSystem/thcc-nationality-race",
                                       self._nationality_code)
                            ]
                        }
                    }
                ]
            })
        if self._occupational_code is not None:
            extensions.append({
                "url": "https://sil-th.org/fhir/StructureDefinition/patient-occupation",
                "valueCodeableConcept": {
                    "coding": [
                        Coding("urn:oid:2.16.840.1.113883.2.9.6.2.7",
                               self._occupational_code)
                    ]
                }
            })
        return extensions

    @property
    def maritalStatus(self):
        if self._maritalStatus is None:
            return None
        return {
            "coding": [Coding("http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                              self._maritalStatus.__getstate__())]
        }

    @property
    def managingOrganization(self):
        return {
            "reference": self._managingOrganizationURL
        }


class PatientBuilder(Builder[ Patient]):
    def __init__(self):
        super().__init__(Patient)

    def from_raw(self, pid:str, name:str, surname:str):
        self._product._personal_id = pid
        self._product._name = name
        self._product._surname = surname
        return self

    def from_csop(self, item: BillTransItem):
        self._product._personal_id = item.pid
        self._product._hospital_number = item.hn
        self._product._combine_name_surname = item.name
        self._product._member_number = item.member_number
        return self

    def from_43folders(self, item: PersonCsvItem):
        self._product._personal_id = item.citizen_id
        self._product._name = item.name
        self._product._surname = item.surname
        self._product.gender = Gender(int(item.gender_number))
        self._product._maritalStatus = MaritalStatus(int(item.martial_status_number))
        self._product._hospital_number = item.hospital_number
        self._product._nationality_code = item.nationality_code
        self._product._occupational_code = item.occupational_code
        return self

    def from_eclaims(self, item: PatCsvRow):
        self._product._personal_id = item.citizen_id
        self._product._name = item.name
        self._product._surname = item.surname
        self._product.gender = Gender(int(item.gender_number))
        self._product._maritalStatus = MaritalStatus(int(item.martial_status_number))
        self._product._hospital_number = item.hospital_number
        self._product._nationality_code = item.nationality_code
        self._product._occupational_code = item.occupational_code
        return self

    def set_managing_organization_ref(self, organization: Organization):
        self._product._managingOrganizationURL = organization.get_resource_url()
        return self

    def add_general_practitioner_organization_ref(self, organization: Organization):
        self._product.generalPractitioner.append({
            "type": "Organization",
            "identifier": organization.identifier[0]
        })
        return self
