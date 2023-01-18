from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Entry import Entry
from fhir_transformer.FHIR.Patient import Patient
from fhir_transformer.FHIR.supports.support import Builder
from fhir_transformer.eclaims.files.E_11ChtCsv import ChtCsvRow
from fhir_transformer.eclaims.files.E_1InsCsv import InsCsvRow


class Coverage(FHIRResource):
    def __getstate__(self):
        return super().__getstate__()

    def __init__(self):
        super(Coverage, self).__init__(resource_type="Coverage")
        self._personal_id: str | None = None
        self._patient_url: str | None = None
        self._insurance_type: str | None = None
        self._main_hospital_code: str | None = None
        self._primary_care_hospital_code: str | None = None
        self._expiration_date: str | None = None
        self._subtype: str | None = None
        self._patient_type: str | None = None

    def create_entry(self) -> Entry:
        entry = Entry(self.get_resource_id_url(), self, {
            "method": "PUT",
            "url": self.get_resource_id_url(),
            "ifNoneExist": self.id
        })
        return entry

    @property
    def id(self):
        return f"Coverage-{self._personal_id}"

    def get_resource_id_url(self) -> str:
        return f"{self.resourceType}/{self.id}"

    @property
    def extension(self):
        return [{
            "url": "https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-coverage-contracted-provider",
            "extension": [
                {
                    "url": "type",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://terms.sil-th.org/CodeSystem/cs-meta-provider-type-coverage",
                                "code": "primary",
                                "display": "สถานบริการหลัก"
                            }
                        ]
                    }
                },
                {
                    "url": "provider",
                    "valueReference": {
                        "identifier": {
                            "system": "https://terms.sil-th.org/id/th-moph-hcode",
                            "value": f"{self._main_hospital_code}"
                        }
                    }
                }
            ]
        }, {
            "url": "https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-coverage-contracted-provider",
            "extension": [
                {
                    "url": "type",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://terms.sil-th.org/CodeSystem/cs-meta-provider-type-coverage",
                                "code": "primary-care",
                                "display": "สถานบริการปฐมภูมิ"
                            }
                        ]
                    }
                },
                {
                    "url": "provider",
                    "valueReference": {
                        "identifier": {
                            "system": "https://terms.sil-th.org/id/th-moph-hcode",
                            "value": f"{self._primary_care_hospital_code}"
                        },
                        "display": "สถานพยาบาลปฐมภูมิ"
                    }
                }
            ]
        }]
    status = "active"
    @property
    def type(self):
        return {
            "coding": [
                {
                    "system": "https://terms.sil-th.org/ValueSet/vs-eclaim-coverage-use",
                    "code": f"{self._insurance_type}"
                }
            ]
        }

    @property
    def beneficiary(self):
        return {
            "reference": f"{self._patient_url}"
        }

    @property
    def period(self):
        return {
            "end": f"{self._expiration_date}"
        }

    @property
    def payor(self):
        return [
            {
                "type": "Organization",
                "display": f"{self._insurance_type}"
            }
        ]

    @property
    def class_(self):
        return [
    {
      "type": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
            "code": "subplan"
          }
        ]
      },
      "value": f"{self._subtype}"
    },
    {
      "type": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
            "code": "subplan"
          }
        ]
      },
      "value": f"{self._patient_type}"
    }
  ]

class CoverageBuilder(Builder[Coverage]):
    def __init__(self):
        super().__init__(Coverage)
    def from_eclaims(self, _1ins_row: InsCsvRow, _11cht_row: ChtCsvRow):
        self._product._personal_id = _1ins_row.citizen_id
        self._product._insurance_type = _1ins_row.insurance_type
        self._product._main_hospital_code = _1ins_row.main_hospital_code
        self._product._primary_care_hospital_code = _1ins_row.primary_care_hospital_code
        #self._product._expiration_date = _1ins_row.dateexp ข้อมูลตัวอย่างไม่มี
        self._product._subtype = _1ins_row.subtype
        self._product._patient_type = _11cht_row.patient_type
        return self

    def set_beneficiary_ref(self, patient: Patient):
        self._product._patient_url = patient.get_resource_url()
        return self