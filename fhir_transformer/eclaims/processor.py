from dataclasses import dataclass
from os import PathLike

from fhir_transformer.FHIR.MedicationDispense import MedicationDispenseBuilder
from fhir_transformer.FHIR.Organization import Organization
from fhir_transformer.FHIR.Patient import PatientBuilder
from fhir_transformer.eclaims.files.E_11ChtCsv import open_cht_csv, ChtCsvRow
from fhir_transformer.eclaims.files.E_3OpdCsv import open_opd_csv, OpdCsvRow
from fhir_transformer.eclaims.files.E_4OrsCsv import open_ors_csv, OrsCsvRow
from fhir_transformer.eclaims.files.E_16DruCsv import open_dru_csv, DruCsvRow
from fhir_transformer.eclaims.files.E_1InsCsv import open_ins_csv, InsCsvRow
from fhir_transformer.eclaims.files.E_2PatCsv import open_pat_csv, PatCsvRow
from fhir_transformer.eclaims.files.E_5OdxCsv import open_odx_csv, OdxCsvRow
from fhir_transformer.eclaims.files.E_6OopCsv import open_oop_csv
from fhir_transformer.models.result import BundleResult
from fhir_transformer.utilities.processing import send_singletype_bundle


@dataclass
class SequenceRow:
    row_1ins: InsCsvRow
    row_2pat: PatCsvRow
    row_3opd: OpdCsvRow
    row_4ors: OrsCsvRow
    row_5odx: OdxCsvRow
    row_11cht: ChtCsvRow
    row_16dru: DruCsvRow


def process_all(_1ins_path: PathLike, _2pat_path:PathLike, _3opd_path:PathLike, _4ors_path:PathLike,
                _5odx_path: PathLike, _6oop_path:PathLike, _11cht_path: PathLike, _16dru_path:PathLike):
    processed_results = list[BundleResult]()

    _1ins_rows = open_ins_csv(_1ins_path)
    _2pat_rows = open_pat_csv(_2pat_path)
    _3opd_rows = open_opd_csv(_3opd_path)
    _4ors_rows = open_ors_csv(_4ors_path)
    _5odx_rows = open_odx_csv(_5odx_path)
    _6oop_rows = open_oop_csv(_6oop_path)

    _11cht_rows = open_cht_csv(_11cht_path)
    _16dru_rows = open_dru_csv(_16dru_path)

    sequence_dict = dict(str, SequenceRow)

    for row in _1ins_rows:
        if sequence_dict[row.sequence] is None:
            o = SequenceRow()
            o.row_1ins = row
        else:
            sequence_dict[row.sequence].row_1ins = row

    for row in _2pat_rows:
        if sequence_dict[row.sequence] is None:
            o = SequenceRow()
            o.row_2pat = row
        else:
            sequence_dict[row.sequence].row_2pat = row

    for row in _3opd_rows:
        if sequence_dict[row.sequence] is None:
            o = SequenceRow()
            o.row_3opd = row
        else:
            sequence_dict[row.sequence].row_3opd = row

    for row in _4ors_rows:
        if sequence_dict[row.sequence] is None:
            o = SequenceRow()
            o.row_4ors = row
        else:
            sequence_dict[row.sequence].row_4ors = row

    for row in _5odx_rows:
        if sequence_dict[row.sequence] is None:
            o = SequenceRow()
            o.row_5odx = row
        else:
            sequence_dict[row.sequence].row_5odx = row

    for row in _11cht_rows:
        if sequence_dict[row.sequence] is None:
            o = SequenceRow()
            o.row_11cht = row
        else:
            sequence_dict[row.sequence].row_11cht = row

    for row in _16dru_rows:
        if sequence_dict[row.sequence] is None:
            o = SequenceRow()
            o.row_16dru = row
        else:
            sequence_dict[row.sequence].row_16dru = row

    # Organization
    unique_hosp_code = set([item.main_hospital_code for item in _1ins_rows])
    send_singletype_bundle(
        [Organization(hospital_code, hospital_code, hospital_code) for hospital_code in unique_hosp_code],
        processed_results)

    patients = []
    for sequence,matched in sequence_dict.items():
        # Patient
        patient_builder = PatientBuilder()
        patient_builder.from_eclaims(matched.row_2pat)
        patient_builder.set_managing_organization_ref()
        patient_builder.add_general_practitioner_organization_ref()
        patient = patient_builder.product
        patients.append(patient)
        # Coverage

        # Diagnosis

    return processed_results

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


#def process_all(ins_csv_path: PathLike, pat_csv_path: PathLike) -> list[BundleResult]:
#    return [*process_ins_csv_path(ins_csv_path),
#            *process_pat_csv_path(pat_csv_path)]
