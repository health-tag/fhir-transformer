from fhir_transformer.FHIR.Patient import PatientBuilder
from fhir_transformer.eclaims.reader import open_pat_csv
from fhir_transformer.models.result import BundleResult
from fhir_transformer.utilities.processing import send_singletype_bundle


def process_pat_csv_path(path: str) -> list[BundleResult]:
    processed_results = list[BundleResult]()
    pat_csv_items = open_pat_csv(path)
    patient_builder = PatientBuilder()
    send_singletype_bundle([patient_builder.from_eclaims(item).product.create_entry() for item in pat_csv_items],
                           processed_results)
    return processed_results


def process_all(pat_csv_path: str) -> list[BundleResult]:
    return [*process_pat_csv_path(pat_csv_path)]
