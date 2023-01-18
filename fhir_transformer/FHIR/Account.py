from abc import ABCMeta

from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Entry import Entry
from fhir_transformer.FHIR.Organization import Organization
from fhir_transformer.FHIR.supports.support import Builder
from fhir_transformer.eclaims.files.E_3OpdCsv import OpdCsvRow


class Account(FHIRResource, metaclass=ABCMeta):
    def __getstate__(self):
        return super().__getstate__()

    @property
    def id(self):
        return f"Account-{self._vn}"

    def create_entry(self) -> Entry:
        entry = Entry(self.get_resource_url(), self, {
            "method": "PUT",
            "url": self.get_resource_url(),
            "ifNoneExist": self.id
        })
        return entry

    def get_resource_url(self):
        return f"{self.resourceType}/{self.id}"

    def __init__(self):
        super(Account, self).__init__(resource_type="Account")
        self._opd_uuc : str |None = None
        self._vn : str |None = None
        self._hospital_code : str |None = None
        self._dateopd : str |None = None
        self._timeopd : str |None = None
        self._fhir_patient_id : str |None = None

    @property
    def extension(self):
        return [
    {
      "url": "https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-account-coverage-use",
      "valueCodeableConcept": {
        "coding": [
          {
            "system": "https://terms.sil-th.org/CodeSystem/cs-43plus-coverage-use",
            "code": f"{self._opd_uuc}",
            "display": "ใช้สิทธิ"
          }
        ]
      }
    }
  ]

    @property
    def identifier(self):
        return [
    {
      "type": {
        "coding": [
          {
            "system": "https://terms.sil-th.org/CodeSystem/cs-th-identifier-type",
            "code": "localVn"
          }
        ]
      },
      "system": f"https://terms.sil-th.org/hcode/5/{self._hospital_code}/VN",
      "value": f"{self._vn}"
    }
  ]

    status = "active"

    @property
    def subject(self):
        return {
            "reference": f"Patient/{self._fhir_patient_id}"
    }
    @property
    def servicePeriod(self):
        return {
            "start": f"{self._dateopd}"
        }
class AccountBuilder(Builder[Account]):
    def __init__(self):
        super().__init__(Account)
    def from_eclaims(self, _3opdCsvRow: OpdCsvRow):
        self._product._opd_uuc = _3opdCsvRow.uuc
        self._product._vn = _3opdCsvRow.sequence
        self._product._dateopd = _3opdCsvRow.dateopd
        self._product._timeopd = _3opdCsvRow.timeopd

    def set_hospital_code(self, organization: Organization):
        self._product._hospital_code = organization._hospital_code

    def add_patient_reference(self, patient: Patient):
        self._product._hospital_code = patient.id
