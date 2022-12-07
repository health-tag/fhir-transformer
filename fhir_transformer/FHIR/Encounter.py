from abc import ABCMeta

from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Entry import Entry
from fhir_transformer.FHIR.Organization import Organization
from fhir_transformer.FHIR.Patient import Patient
from fhir_transformer.FHIR.Practitioner import Practitioner
from fhir_transformer.FHIR.supports.support import Coding, Identifier, Builder
from fhir_transformer.csop.files.billdisp import DispensingItemRow
from fhir_transformer.mapping_keys.csop import disp_status_mapping

encounter_identifier_system = "https://sil-th.org/CSOP/dispenseId"


class Encounter(FHIRResource, metaclass=ABCMeta):
    status = "finished"
    _reserved_class = Coding("http://terminology.hl7.org/CodeSystem/v3-ActCode", "AMB", "ambulatory")

    def __init__(self):
        super().__init__(resource_type="Encounter")
        self._patient_hospital_number: str | None = None
        self._patientURL: str | None = None
        self.participant = list[dict[str, dict[str, str]]]()
        self._practitionerURL: str | None = None
        self._serviceProviderURL: str | None = None

    def __getstate__(self):
        return super().__getstate__()


class EncounterDispensing(Encounter):
    def __getstate__(self):
        return super().__getstate__()

    def __init__(self):
        super().__init__()
        self._disp_id: str | None = None
        self._presc_date: str | None = None
        self._disp_date: str | None = None
        self._disp_status: str | None = None

    def create_entry(self) -> Entry:
        entry = Entry(self.get_resource_id_url(), self, {
            "method": "PUT",
            "url": self.get_resource_id_url(),
            "ifNoneExist": self.id # f"identifier={self.identifier[0].get_string_for_reference()}"
        })
        return entry

    @property
    def id(self):
        return f"DISPENSING-{self.create_id(self._disp_id)}"

    def get_resource_url(self):
        return f"{self.resourceType}?identifier={self.identifier[0].get_string_for_reference()}"

    def get_resource_id_url(self):
        return f"{self.resourceType}/{self.id}"

    @property
    def text(self) -> dict[str, str]:
        return {
            "status": "extensions",
            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Dispense ID: {self._disp_id} (HN: {self._patient_hospital_number})<p>service: Pharmacy | status: {disp_status_mapping[self._disp_status]}</p></div>"
        }

    @property
    def identifier(self):
        return [Identifier(encounter_identifier_system, f"{self._disp_id}")]

    serviceType = {
        "coding": [Coding("http://terminology.hl7.org/CodeSystem/service-type", "64", "Pharmacy")]
    }

    @property
    def subject(self) -> dict[str, str]:
        return {
            "reference": self._patientURL
        }

    @property
    def period(self) -> dict[str, str]:
        return {
            "start": f"{self._presc_date}",
            "end": f"{self._disp_date}"
        }

    @property
    def serviceProvider(self) -> dict[str, str]:
        return {
            "reference": self._serviceProviderURL
        }


class EncounterDispensingBuilder(Builder[EncounterDispensing]):
    def __init__(self):
        super().__init__(EncounterDispensing)

    def from_raw(self, disp_id: str, presc_date: str, disp_date: str, disp_status: str):
        self._product._disp_id = disp_id
        self._product._presc_date = presc_date
        self._product._disp_date = disp_date
        self._product._disp_status = disp_status
        return self

    def from_csop(self, item: DispensingItemRow):
        self._product._disp_id = item.disp_id
        self._product._presc_date = item.presc_date
        self._product._disp_date = item.disp_date
        self._product._disp_status = item.disp_status
        return self

    def set_patient_ref(self, patient: Patient):
        self._product._patientURL = patient.get_resource_id_url()
        self._product._patient_hospital_number = patient._hospital_number
        return self

    def add_participant_ref(self, practitioner: Practitioner):
        self._product.participant.append({
            "individual": {
                "reference": practitioner.get_resource_id_url()
            }
        })
        return self

    def set_serviceProvider_ref(self, organization: Organization):
        self._product._serviceProviderURL = organization.get_resource_url()
        return self
