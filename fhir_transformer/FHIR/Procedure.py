from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Entry import Entry


class Procedure(FHIRResource):
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

    def set_encounter_ref(self, encounter: EncounterDispensing):
        self._product._encounterURL = encounter.get_resource_id_url()
        return self