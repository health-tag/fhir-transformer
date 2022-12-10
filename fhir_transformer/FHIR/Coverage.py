from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Entry import Entry


class Coverage(FHIRResource):
    def __getstate__(self):
        return super().__getstate__()

    def __init__(self, personal_id: str):
        super(Coverage, self).__init__(resource_type="Coverage")
        self._personal_id = personal_id
        self._patient_url: str | None = None

    def create_entry(self) -> Entry:
        entry = Entry(self.get_resource_id_url(), self, {
            "method": "PUT",
            "url": f"Location?identifier=https://sil-th.org/CSOP/station|{self._station}",
            "ifNoneExist": f"identifier=https://sil-th.org/CSOP/station|{self._station}"
        })
        return entry

    def get_resource_id_url(self) -> str:
        return f"{self.resourceType}/{self.id}"

    @property
    def extension(self):
        return [{"url": "https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-coverage-contracted-provider",
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
              "value": "35241" //01.INS.HOSPMAIN
            }
          }
        }
      ]},{      "url": "https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-coverage-contracted-provider",
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
              "value": "14971" //01.INS.HOSPSUB
            },
            "display": "สถานพยาบาลปฐมภูมิ"
          }
        }
      ]}]

    status: str = "active",

    @property
    def type(self):
        return {
            "coding":[
                {
                    "system": "https://terms.sil-th.org/ValueSet/vs-eclaim-coverage-use",
                    "code": "UCS" // 01.INS.INSCL
                }
            ]
        }

    @property
    def beneficiary(self):
        return {
            "reference": self._patient_url
        }

    @property
    def period(self):
        return {
    "end": "2070-09-30" //01.INS.DATEEXP
  }

    @property
    def payor(self):

    @property
    def identifier(self) -> list[dict[str, str]]:
        return [
            {
                "system": "https://www.dopa.go.th",
                "value": f"{self._personal_id}"
            }
        ]


    '''
    @property
    def text(self) -> dict[str, str]:
        return {
            "status": "generated",
            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Station ID: {self._station}</div>"
        }


    @property
    def type(self) -> list[dict[str, list[dict[str, str]]]]:
        return [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                        "code": "BILL",
                        "display": "Billing Contact"
                    }
                ]
            }
        ]

    @property
    def managingOrganization(self) -> dict[str, str]:
        return {
            "reference": f"Organization/{self._hospital_blockchain_address}"
        }
    '''
