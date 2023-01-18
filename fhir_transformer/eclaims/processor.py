from dataclasses import dataclass
from os import PathLike

from fhir_transformer.FHIR.Account import AccountBuilder
from fhir_transformer.FHIR.Coverage import CoverageBuilder
from fhir_transformer.FHIR.MedicationDispense import MedicationDispenseBuilder
from fhir_transformer.FHIR.Organization import Organization
from fhir_transformer.FHIR.Patient import PatientBuilder, Patient
from fhir_transformer.eclaims.files.E_11ChtCsv import open_cht_csv, ChtCsvRow
from fhir_transformer.eclaims.files.E_3OpdCsv import open_opd_csv, OpdCsvRow
from fhir_transformer.eclaims.files.E_4OrfCsv import open_orf_csv, OrfCsvRow
from fhir_transformer.eclaims.files.E_16DruCsv import open_dru_csv, DruCsvRow
from fhir_transformer.eclaims.files.E_1InsCsv import open_ins_csv, InsCsvRow
from fhir_transformer.eclaims.files.E_2PatCsv import open_pat_csv, PatCsvRow
from fhir_transformer.eclaims.files.E_5OdxCsv import open_odx_csv, OdxCsvRow
from fhir_transformer.eclaims.files.E_6OopCsv import open_oop_csv
from fhir_transformer.models.result import BundleResult
from fhir_transformer.utilities.processing import send_singletype_bundle, bundle_cycler
from typing import Optional

@dataclass
class JoinedOpd:
    row_1ins: Optional[InsCsvRow] = None
    #row_2pat: Optional[PatCsvRow]= None
    row_3opd: Optional[OpdCsvRow]= None
    row_4orf: Optional[OrfCsvRow]= None
    row_5odx: Optional[OdxCsvRow]= None
    row_6oop: Optional[OdxCsvRow]= None
    row_11cht: Optional[ChtCsvRow]= None
    row_16dru: Optional[DruCsvRow]= None


def process_all(processed_results: list[BundleResult],_1ins_path: PathLike, _2pat_path:PathLike, _3opd_path:PathLike, _4orf_path:PathLike,
                _5odx_path: PathLike, _6oop_path:PathLike, _11cht_path: PathLike, _16dru_path:PathLike):

    _1ins_rows = open_ins_csv(_1ins_path)
    _2pat_rows = open_pat_csv(_2pat_path)
    _3opd_rows = open_opd_csv(_3opd_path)
    _4orf_rows = open_orf_csv(_4orf_path)
    _5odx_rows = open_odx_csv(_5odx_path)
    _6oop_rows = open_oop_csv(_6oop_path)

    _11cht_rows = open_cht_csv(_11cht_path)
    _16dru_rows = open_dru_csv(_16dru_path)

    joined_opd_files : dict[str, JoinedOpd]= dict()

    for row in _1ins_rows:
        if row.sequence not in joined_opd_files:
            o = JoinedOpd()
            o.row_1ins = row
            joined_opd_files[row.sequence] = o
        else:
            joined_opd_files[row.sequence].row_1ins = row

    #for row in _2pat_rows:
    #    if row.sequence not in joined_opd_files:
    #        o = JoinedOpd()
    #        o.row_2pat = row
    #    else:
    #        joined_opd_files[row.sequence].row_2pat = row

    for row in _3opd_rows:
        if row.sequence not in joined_opd_files:
            o = JoinedOpd()
            o.row_3opd = row
            joined_opd_files[row.sequence] = o
        else:
            joined_opd_files[row.sequence].row_3opd = row

    for row in _4orf_rows:
        if row.sequence not in joined_opd_files:
            o = JoinedOpd()
            o.row_4orf = row
            joined_opd_files[row.sequence] = o
        else:
            joined_opd_files[row.sequence].row_4orf = row

    for row in _5odx_rows:
        if row.sequence not in joined_opd_files:
            o = JoinedOpd()
            o.row_5odx = row
            joined_opd_files[row.sequence] = o
        else:
            joined_opd_files[row.sequence].row_5odx = row

    for row in _6oop_rows:
        if row.sequence not in joined_opd_files:
            o = JoinedOpd()
            o.row_6oop = row
            joined_opd_files[row.sequence] = o
        else:
            joined_opd_files[row.sequence].row_6oop = row

    for row in _11cht_rows:
        if row.sequence not in joined_opd_files:
            o = JoinedOpd()
            o.row_11cht = row
            joined_opd_files[row.sequence] = o
        else:
            joined_opd_files[row.sequence].row_11cht = row

    for row in _16dru_rows:
        if row.sequence not in joined_opd_files:
            o = JoinedOpd()
            o.row_16dru = row
            joined_opd_files[row.sequence]=o
        else:
            joined_opd_files[row.sequence].row_16dru = row

    # Organization
    unique_hosp_code = set([item.main_hospital_code for item in _1ins_rows])
    organizations = [Organization(hospital_code, hospital_code, hospital_code) for hospital_code in unique_hosp_code]
    organizations_dict = dict(zip(unique_hosp_code, organizations))
    send_singletype_bundle(
        organizations,
        processed_results)

    # Patient
    patients_dict : dict[str, Patient]= dict()
    patient_builder = PatientBuilder()
    for row in _2pat_rows:
        patient_builder.from_eclaims(row)
        for org in organizations:
            if org._hospital_code == row.hospital_code:
                patient_builder.set_managing_organization_ref(org)
        patients_dict[row.hospital_number]= patient_builder.product

    coverages = []
    accounts = []
    coverage_builder = CoverageBuilder()
    account_builder = AccountBuilder()
    for sequence,matched in joined_opd_files.items():
        # Coverage
        if matched.row_1ins is not None and matched.row_11cht is not None:
            coverage_builder.from_eclaims(matched.row_1ins, matched.row_11cht)
            coverage_builder.set_beneficiary_ref(patients_dict[matched.row_1ins.hospital_number])
            coverages.append(coverage_builder.product)
        # Account
        if matched.row_3opd is not None:
            account_builder.from_eclaims(matched.row_3opd)
            account_builder.set_hospital_code(organizations_dict[matched.row_3opd.hospital_number])
            accounts.append(account_builder.product)

    bundle_cycler(patients_dict.values(), processed_results)
    bundle_cycler(coverages, processed_results)
    bundle_cycler(accounts, processed_results)
    return processed_results