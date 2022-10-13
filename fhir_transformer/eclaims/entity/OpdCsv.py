from dataclasses import dataclass

from fhir_transformer.FHIR.Observation import RespiratoryRateObservation

@dataclass
class OpdCsvItem:
    service_id:str
    effective_datetime:str
    respiratory_rate:str