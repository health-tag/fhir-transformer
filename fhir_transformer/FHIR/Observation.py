from abc import ABCMeta
from enum import Enum

from fhir_transformer.FHIR import Encounter
from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Encounter import encounter_identifier_system
from fhir_transformer.FHIR.Patient import patient_HN_identifier_system, Patient
from fhir_transformer.FHIR.supports.support import Coding
from fhir_transformer.eclaims.files.E_3OpdCsv import OpdCsvRow


class ObservationType(Enum):
    BloodPressure = 0
    RespiratoryRate = 1
    HeartRate = 2
    BodyTemperature = 3


class ObservationBuilder:
    def __init__(self):
        self._product = None

    def create(self, observation_type: ObservationType):
        match observation_type:
            case ObservationType.BloodPressure:
                self._product = BloodPressureObservation()
            case ObservationType.RespiratoryRate:
                self._product = RespiratoryRateObservation()
            case ObservationType.HeartRate:
                self._product = HeartRateObservation()
            case ObservationType.BodyTemperature:
                self._product = BodyTemperatureObservation()
        return self

    def from_eclaim_opd_csv(self, item: OpdCsvRow):
        self._product._service_id = item.service_id
        self._product.effective_datetime = item.effective_datetime
        if type(self._product) is BloodPressureObservation:
            obj: BloodPressureObservation = self._product
            obj._systolic_blood_pressure = int(item.respiratory_rate)
            obj._diastolic_blood_pressure = int(item.respiratory_rate)
        if type(self._product) is RespiratoryRateObservation:
            obj: RespiratoryRateObservation = self._product
            obj._respiratory_rate = int(item.respiratory_rate)
        if type(self._product) is HeartRateObservation:
            obj: HeartRateObservation = self._product
            obj._heart_rate = int(item.respiratory_rate)
        if type(self._product) is BodyTemperatureObservation:
            obj: BodyTemperatureObservation = self._product
            obj._body_temperature = int(item.respiratory_rate)
        return self

    def set_patient_ref(self, patient: Patient):
        for identifier in patient.identifier:
            if identifier.system == patient_HN_identifier_system:
                self._product.subject = {
                    "reference": f"{patient.resourceType}/{patient.id}"
                }
        return self

    def set_encounter_ref(self, encounter: Encounter):
        for identifier in encounter.identifier:
            if identifier.system == encounter_identifier_system:
                self._product.encounter = {
                    "reference": f"{encounter.resourceType}?identifier={identifier.get_string_for_reference()}"
                }
        return self

    def get_product(self):
        return self._product


class Observation(FHIRResource, metaclass=ABCMeta):

    def __init__(self):
        super(Observation, self).__init__(resource_type="Observation")
        self.effective_datetime: str | None = None
        self._service_id = None
        #self.subject = None
        #self.encounter = None

    @property
    def identifier(self):
        return [
            {
                "system": "https://sil-th.org/fhir/Id/service-id",
                "value": f"{self._service_id}"
            }
        ]

    status = "final"

    '''
    "performer":  [
        {
            "identifier": {
                "system": "https://sil-th.org/fhir/CodeSystem/eclaim-clinic",
                "value": "00100"
            }
        }
    ],
    '''


class VitalSignObservation(Observation, metaclass=ABCMeta):
    category = [
        {
            "coding": [
                Coding("http://terminology.hl7.org/CodeSystem/observation-category", "vital-signs", "Vital Signs")],
            "text": "Vital Signs"
        }
    ]


class RespiratoryRateObservation(VitalSignObservation, Observation):
    def __getstate__(self):
        return super().__getstate__()

    def __init__(self):
        super().__init__()
        self._respiratory_rate: int | None = None

    meta = {
        "profile": [
            "https://sil-th.org/fhir/StructureDefinition/eclaim-observation-rr",
            "http://hl7.org/fhir/StructureDefinition/resprate",
            "http://hl7.org/fhir/StructureDefinition/vitalsigns"
        ]
    }

    code = {
               "coding": [Coding("http://loinc.org", "9279-1", "Respiratory rate")],
               "text": "Respiratory rate"
           },

    @property
    def valueQuantity(self):
        return {
            "value": self._respiratory_rate,
            "unit": "breaths/minute",
            "system": "http://unitsofmeasure.org",
            "code": "/min"
        }


class HeartRateObservation(VitalSignObservation, Observation):
    def __getstate__(self):
        return super().__getstate__()

    def __init__(self):
        super().__init__()
        self._effective_datetime: str | None = None
        self._heart_rate: int | None = None

    meta = {
        "profile": [
            "https://sil-th.org/fhir/StructureDefinition/eclaim-observation-pr",
            "http://hl7.org/fhir/StructureDefinition/heartrate",
            "http://hl7.org/fhir/StructureDefinition/vitalsigns"
        ]
    }

    code = {
               "coding": [Coding("http://loinc.org", "8867-4", "Heart rate")],
               "text": "Heart rate"
           },

    @property
    def valueQuantity(self):
        return {
            "value": self._heart_rate,
            "unit": "beats/minute",
            "system": "http://unitsofmeasure.org",
            "code": "/min"
        }


class BloodPressureObservation(VitalSignObservation, Observation):
    def __getstate__(self):
        return super().__getstate__()

    def __init__(self):
        super().__init__()
        self._effective_datetime: str | None = None
        self._systolic_blood_pressure: int | None = None
        self._diastolic_blood_pressure: int | None = None

    meta = {
        "profile": [
            "https://sil-th.org/fhir/StructureDefinition/eclaim-observation-pr",
            "http://hl7.org/fhir/StructureDefinition/bp",
            "http://hl7.org/fhir/StructureDefinition/vitalsigns"
        ]
    }

    code = {
               "coding": [Coding("http://loinc.org", "85354-9")],
               "text": "Blood pressure"
           },

    @property
    def component(self):
        return [
            {
                "code": {
                    "coding": [Coding("http://loinc.org", "8480-6", "Systolic blood pressure")],
                    "text": "Systolic blood pressure"
                },
                "valueQuantity": {
                    "value": self._systolic_blood_pressure,
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            },
            {
                "code": {
                    "coding": [Coding("http://loinc.org", "85354-9", "Diastolic blood pressure")],
                    "text": "Diastolic blood pressure"
                },
                "valueQuantity": {
                    "value": self._diastolic_blood_pressure,
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            }
        ]


class BodyTemperatureObservation(VitalSignObservation, Observation):
    def __getstate__(self):
        return super().__getstate__()

    def __init__(self):
        super().__init__()
        self._effective_datetime: str | None = None
        self._body_temperature: int | None = None

    meta = {
        "profile": [
            "https://sil-th.org/fhir/StructureDefinition/eclaim-observation-pr",
            "http://hl7.org/fhir/StructureDefinition/bodytemp",
            "http://hl7.org/fhir/StructureDefinition/vitalsigns"
        ]
    }

    code = {
               "coding": [Coding("http://loinc.org", "8310-5", "Body temperature")],
               "text": "Body temperature"
           },

    @property
    def valueQuantity(self):
        return {
            "value": self._body_temperature,
            "unit": "°C",
            "system": "http://unitsofmeasure.org",
            "code": "Cel"
        }
