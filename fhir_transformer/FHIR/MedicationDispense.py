from typing import Dict

from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Encounter import Encounter, EncounterDispensing
from fhir_transformer.FHIR.Entry import Entry
from fhir_transformer.FHIR.Organization import Organization
from fhir_transformer.FHIR.Patient import Patient
from fhir_transformer.FHIR.Practitioner import Practitioner
from fhir_transformer.FHIR.supports.support import Builder, Identifier, Coding
from fhir_transformer.csop.holder.billdisp import DispensingItemDetailRow, DispensingItemRow
from fhir_transformer.mapping_keys.csop import disp_status_mapping


class MedicationDispense(FHIRResource):
    def __getstate__(self):
        return super().__getstate__()

    def __init__(self):
        super().__init__(resource_type="MedicationDispense")
        self._disp_id: str | None = None
        self._disp_status: str | None = None
        self._local_drug_id: str | None = None
        self._standard_drug_id: str | None = None
        self._product_cat: str | None = None
        self._dfs: str | None = None
        self._quantity: str | None = None
        self._package_size: str | None = None
        self._instruction_text: str | None = None
        self._instruction_code: str | None = None
        self.whenHandedOver: str | None = None

        self._patient_hospital_number: str | None = None

        self.performer = list[dict[str, dict[str, str]]]()
        self._patientURL: str | None = None
        self._encounterURL: str | None = None

    def create_entry(self) -> Entry:
        entry = Entry(f"MedicationDispense/{self._disp_id}|{self._local_drug_id}", self, {
            "method": "PUT",
            "url": f"MedicationDispense?identifier=https://sil-th.org/CSOP/dispenseId|{self._disp_id}&code=https://sil-th.org/CSOP/localCode|{self._local_drug_id}",
            "ifNoneExist": f"identifier=https://sil-th.org/CSOP/dispenseId|{self._disp_id}&code=https://sil-th.org/CSOP/localCode|{self._local_drug_id}"
        })
        return entry

    def get_resource_url(self) -> str:
        return f"{self.resourceType}?identifier={self.identifier[0].get_string_for_reference()}"

    @property
    def text(self) -> dict[str, str]:
        return {
            "status": "extensions",
            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Dispense ID: {self._disp_id} (HN: {self._patient_hospital_number})<p>{self._dfs} - {self._instruction_text}</p><p>QTY: {self._quantity} {self._package_size}</p></div>"
        }

    @property
    def extension(self) -> list[dict[str, str | dict[str, str]]]:
        return [
            {
                "url": "https://sil-th.org/fhir/StructureDefinition/product-category",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "https://sil-th.org/fhir/CodeSystem/csop-productCategory",
                            "code": f"{self._product_cat}"
                        }
                    ]
                }
            },
        ]

    @property
    def identifier(self) -> list[Identifier]:
        return [Identifier("https://sil-th.org/CSOP/dispenseId", f"{self._disp_id}")]

    @property
    def status(self) -> str:
        return f"{disp_status_mapping[self._disp_status]}"

    category = {
        "coding": [
            {
                "system": "http://terminology.hl7.org/fhir/CodeSystem/medicationdispense-category",
                "code": "outpatient"
            }
        ]
    }

    @property
    def medicationCodeableConcept(self) -> dict[str, str]:
        return {
            "coding": [Coding("https://sil-th.org/CSOP/localCode", self._local_drug_id),
                       Coding("https://tmt.this.or.th", self._standard_drug_id)],
            "text": f"{self._dfs}"
        }

    @property
    def subject(self) -> dict[str, str]:
        return {
            "reference": self._patientURL
        }

    @property
    def context(self) -> dict[str, str]:
        return {
            "reference": self._encounterURL
        }

    @property
    def quantity(self) -> dict[str, str | None]:
        return {
            "value": int(self._quantity),
            "unit": self._package_size
        }

    @property
    def dosageInstruction(self) -> list[dict[str, str]]:
        return [
            {
                "text": f"{self._instruction_text}",
                "timing": {
                    "code": {
                        "text": f"{self._instruction_code}"
                    }
                }
            }
        ]


class MedicationDispenseBuilder(Builder[MedicationDispense]):
    def __init__(self):
        super().__init__(MedicationDispense)
    def from_raw(self, disp_id:str, disp_status:str, local_drug_id, standard_drug_id:str, product_cat:str,dfs:str,quantity:str, package_size:str,instruction_text:str,instruction_code:str,disp_date:str):
        self._product._disp_id = disp_id
        self._product._disp_status = disp_status
        self._product._local_drug_id = local_drug_id
        self._product._standard_drug_id = standard_drug_id
        self._product._product_cat = product_cat
        self._product._dfs = dfs
        self._product._quantity = quantity
        self._product._package_size = package_size
        self._product._instruction_text = instruction_text
        self._product._instruction_code = instruction_code
        self._product.whenHandedOver = disp_date

        return self

    def from_csop(self, item: DispensingItemRow, detail: DispensingItemDetailRow):
        self._product._disp_id = detail.disp_id
        self._product._disp_status = item.disp_status
        self._product._local_drug_id = detail.local_drug_id
        self._product._standard_drug_id = detail.standard_drug_id
        self._product._product_cat = detail.product_cat
        self._product._dfs = detail.dfs
        self._product._quantity = detail.quantity
        self._product._package_size = detail.package_size
        self._product._instruction_text = detail.instruction_text
        self._product._instruction_code = detail.instruction_code
        self._product.whenHandedOver = item.disp_date

        return self

    def set_patient_ref(self, patient: Patient):
        self._product._patientURL = patient.get_resource_url()
        self._product._patient_hospital_number = patient._hospital_number
        return self

    def set_encounter_ref(self, encounter: EncounterDispensing):
        self._product._encounterURL = encounter.get_resource_url()
        return self

    def add_performer_ref(self, performer: Practitioner | Organization):
        self._product.performer.append({
            "actor": {
                "reference": performer.get_resource_url()
            }
        })
        return self
