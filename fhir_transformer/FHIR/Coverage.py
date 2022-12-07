from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Entry import Entry


class Coverage(FHIRResource):
    def __getstate__(self):
        return super().__getstate__()

    def __init__(self, personal_id: str):
        super(Coverage, self).__init__(resource_type="Coverage")
        self._personal_id = personal_id
        self.meta = Coverage.meta
        self.status = Coverage.status

    def create_entry(self) -> Entry:
        entry = Entry(f"Location?identifier=https://sil-th.org/CSOP/station|{self._station}", self, {
            "method": "PUT",
            "url": f"Location?identifier=https://sil-th.org/CSOP/station|{self._station}",
            "ifNoneExist": f"identifier=https://sil-th.org/CSOP/station|{self._station}"
        })
        return entry

    meta = {
               "profile": [
                   "https://sil-th.org/fhir/StructureDefinition/eclaim-coverage"
               ]
           },

    @property
    def identifier(self) -> list[dict[str, str]]:
        return [
            {
                "system": "https://www.dopa.go.th",
                "value": f"{self._personal_id}"
            }
        ]

    status: str = "active",
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
