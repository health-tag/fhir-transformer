from os import PathLike

from fhir_transformer.FHIR.MedicationDispense import MedicationDispenseBuilder
from fhir_transformer.FHIR.Organization import Organization
from fhir_transformer.FHIR.Patient import PatientBuilder
from fhir_transformer.eclaims.files.DruCsv16 import open_dru_csv
from fhir_transformer.eclaims.files.InsCsv1 import open_ins_csv
from fhir_transformer.eclaims.files.PatCsv2 import open_pat_csv
from fhir_transformer.models.result import BundleResult
from fhir_transformer.utilities.processing import send_singletype_bundle


def process_ins_csv_path(path: PathLike) -> list[BundleResult]:
    processed_results = list[BundleResult]()

    # Organization
    ins_csv_items = open_ins_csv(path)
    unique_hosp_code = set([item.main_hospital_code for item in ins_csv_items])

    send_singletype_bundle(
        [Organization(hospital_code, hospital_code, hospital_code) for hospital_code in unique_hosp_code],
        processed_results)
    return processed_results


def process_pat_csv_path(path: PathLike) -> list[BundleResult]:
    # Builder
    patient_builder = PatientBuilder()

    processed_results = list[BundleResult]()

    # Patient
    pat_csv_items = open_pat_csv(path)
    send_singletype_bundle([patient_builder.from_eclaims(item).product for item in pat_csv_items],
                           processed_results)
    return processed_results


def process_dru_csv_path(path: PathLike) -> list[BundleResult]:
    # Builder
    medication_builder = MedicationDispenseBuilder()

    processed_results = list[BundleResult]()

    # Patient
    dru_csv_items = open_dru_csv(path)
    send_singletype_bundle([medication_builder.from_eclaims(item).product for item in dru_csv_items],
                           processed_results)
    return processed_results


def process_all(ins_csv_path: PathLike, pat_csv_path: PathLike) -> list[BundleResult]:
    return [*process_ins_csv_path(ins_csv_path),
            *process_pat_csv_path(pat_csv_path)]
