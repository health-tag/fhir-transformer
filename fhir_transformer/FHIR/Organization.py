from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Entry import Entry
from fhir_transformer.FHIR.supports.support import Identifier


class Organization(FHIRResource):
    @property
    def name(self) -> str:
        return self._hospital_name

    @property
    def identifier(self):
        return [Identifier("https://bps.moph.go.th/hcode/5", f"{self._hospital_code}"),
                Identifier("https://terms.sil-th.org/id/th-moph-hcode", f"{self._hospital_code}")]

    @property
    def id(self):
        return self._hospital_blockchain_address

    def __init__(self, hospital_name: str, hospital_blockchain_address: str, hospital_code: str):
        super(Organization, self).__init__(resource_type="Organization")
        self._hospital_name = hospital_name
        self._hospital_blockchain_address = hospital_blockchain_address
        self._hospital_code = hospital_code

    def create_entry(self) -> Entry:
        entry = Entry(self.get_resource_id_url(), self, {
            "method": "PUT",
            "url": self.get_resource_id_url(),
            "ifNoneExist": self.id
        })
        return entry

    def get_resource_url(self):
        return f"{self.resourceType}/{self._hospital_blockchain_address}"

    def get_resource_id_url(self):
        return f"{self.resourceType}/{self._hospital_blockchain_address}"

    def __getstate__(self):
        return super().__getstate__()
