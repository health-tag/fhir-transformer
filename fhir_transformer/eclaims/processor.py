import multiprocessing
from dataclasses import dataclass
from os import PathLike

import numpy as np
from fhir.resources.claim import Claim, ClaimInsurance, ClaimItem,ClaimSupportingInfo
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coverage import Coverage, CoverageClass
from fhir.resources.fhirtypes import Id, Code, String, ExtensionType, Uri, Boolean, Decimal, DosageType, \
    MedicationDispensePerformerType
from fhir.resources.humanname import HumanName
from fhir.resources.extension import Extension
from fhir.resources.medicationdispense import MedicationDispense
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.money import Money
from fhir.resources.quantity import Quantity
from fhir.resources.servicerequest import ServiceRequest
# from fhir_transformer.FHIR.Account import AccountBuilder
# from fhir_transformer.FHIR.Coverage import CoverageBuilder
# from fhir_transformer.FHIR.MedicationDispense import MedicationDispenseBuilder
# from fhir_transformer.FHIR.Organization import Organization
# from fhir_transformer.FHIR.Patient import PatientBuilder, Patient

from fhir.resources.organization import Organization
from fhir.resources.identifier import Identifier
from fhir.resources.patient import Patient
from fhir.resources.reference import Reference
from fhir.resources.coding import Coding
from fhir.resources.period import Period
from fhir.resources.account import Account
from fhir.resources.encounter import Encounter, EncounterLocation, EncounterDiagnosis, EncounterHospitalization

from fhir_transformer.eclaims.files.E_11ChtCsv import open_cht_csv, ChtCsvRow
from fhir_transformer.eclaims.files.E_3OpdCsv import open_opd_csv, OpdCsvRow
from fhir_transformer.eclaims.files.E_4OrfCsv import open_orf_csv, OrfCsvRow
from fhir_transformer.eclaims.files.E_16DruCsv import open_dru_csv, DruCsvRow
from fhir_transformer.eclaims.files.E_1InsCsv import open_ins_csv, InsCsvRow
from fhir_transformer.eclaims.files.E_2PatCsv import open_pat_csv, PatCsvRow
from fhir_transformer.eclaims.files.E_5OdxCsv import open_odx_csv, OdxCsvRow
from fhir_transformer.eclaims.files.E_6OopCsv import open_oop_csv
from fhir_transformer.models.result import BundleResult
from fhir_transformer.utilities.processingNext import send_singletype_bundle, bundle_cycler
from typing import Optional


@dataclass
class JoinedOpd:
    row_1ins: Optional[InsCsvRow] = None
    # row_2pat: Optional[PatCsvRow]= None
    row_3opd: Optional[OpdCsvRow] = None
    row_4orf: Optional[OrfCsvRow] = None
    row_5odx: Optional[OdxCsvRow] = None
    row_6oop: Optional[OdxCsvRow] = None
    row_11cht: Optional[ChtCsvRow] = None
    row_16dru: Optional[DruCsvRow] = None


def process_all(processed_results: list[BundleResult], _1ins_path: PathLike, _2pat_path: PathLike, _3opd_path: PathLike,
                _4orf_path: PathLike,
                _5odx_path: PathLike, _6oop_path: PathLike, _11cht_path: PathLike, _16dru_path: PathLike):
    _1ins_rows = open_ins_csv(_1ins_path)
    _2pat_rows = open_pat_csv(_2pat_path)
    _3opd_rows = open_opd_csv(_3opd_path)
    _4orf_rows = open_orf_csv(_4orf_path)
    _5odx_rows = open_odx_csv(_5odx_path)
    _6oop_rows = open_oop_csv(_6oop_path)

    _11cht_rows = open_cht_csv(_11cht_path)
    _16dru_rows = open_dru_csv(_16dru_path)

    joined_opd_files: dict[str, JoinedOpd] = dict()

    for row in _1ins_rows:
        if row.sequence not in joined_opd_files:
            o = JoinedOpd()
            o.row_1ins = row
            joined_opd_files[row.sequence] = o
        else:
            joined_opd_files[row.sequence].row_1ins = row

    # for row in _2pat_rows:
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
            joined_opd_files[row.sequence] = o
        else:
            joined_opd_files[row.sequence].row_16dru = row

    # Organization
    unique_hosp_code = set([item.main_hospital_code for item in _1ins_rows if isinstance(item.main_hospital_code, str)])
    organizations = list[Organization]()
    for hospital_code in unique_hosp_code:
        o: Organization = Organization.construct()
        o.identifier = [Identifier(system="https://www.nhso.go.th", value=hospital_code)]
        o.id = Id(f"hcode-{hospital_code}")
        organizations.append(o)
    organizations_dict = dict(zip(unique_hosp_code, organizations))
    #send_singletype_bundle(organizations, processed_results)

    # Patient
    patients_dict: dict[str, Patient] = dict()
    for row in _2pat_rows:
        patient: Patient = Patient.construct()
        patient.identifier = [
            Identifier(system=Uri("https://www.dopa.go.th"), value=f"{row.citizen_id}"),
            Identifier(system=Uri("https://terms.sil-th.org/id/th-cid"), value=f"{row.hospital_number}"),
            Identifier(system=Uri("https://sil-th.org/fhir/Id/hn"), value=f"{row.hospital_number}"),
        ]
        patient.name = [HumanName(prefix=[String(row.title)], given=[String(row.name)], family=String(row.surname),
                                  text=String(f"{row.title} {row.name} {row.surname}"))]
        patient.gender = Code("M" if row.gender_number == 1 else "F")
        matched_org = organizations_dict[row.hospital_code]
        patient.managingOrganization = Reference(reference=matched_org.relative_path())
        patient.id = Id(f"cid-{row.citizen_id}")

        patients_dict[row.hospital_number] = patient
        for sequence, matched in joined_opd_files.items():
            # Coverage
            if matched.row_1ins is not None and matched.row_11cht is not None:
                coverage: Coverage = Coverage.construct()
                coverage.status = Code("active")
                coverage.type = CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/ValueSet/vs-eclaim-coverage-use"), code=Code(matched.row_1ins.insurance_type))])
                coverage.beneficiary = Reference(reference=patient.relative_path())
                if isinstance(matched.row_1ins.insurance_expired_date,str):
                    coverage.period = Period(end=matched.row_1ins.insurance_expired_date)
                coverage.payor = [Reference(reference=matched_org.relative_path())]
                coverage.class_fhir = [CoverageClass(type=CodeableConcept(coding=[Coding(system=Uri("http://terminology.hl7.org/CodeSystem/coverage-class"), code=Code("subplan"))]), value=String(matched.row_1ins.subtype)),
                                       CoverageClass(type=CodeableConcept(coding=[Coding(system=Uri("http://terminology.hl7.org/CodeSystem/coverage-class"), code=Code("subplan"))]), value=String(matched.row_11cht.patient_type))]
                coverage.extension = [Extension(
                     url=Uri("https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-coverage-contracted-provider"),
                     extension=[
                         Extension(url=Uri("type"), valueCodeableConcept=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-meta-provider-type-coverage"), code=Code("primary"), display=String("สถานบริการหลัก"))])),
                         Extension(url=Uri("provider"), valueIdentifier=Identifier(system=Uri("https://terms.sil-th.org/id/th-moph-hcode"), value=String(matched.row_1ins.main_hospital_code)))
                    ])]
                coverage.id = Id(f"cid-{row.citizen_id}")

            if matched.row_3opd is not None:
                # Account
                account = Account.construct()
                account.status = Code("active")
                account.identifier = [Identifier(type=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-identifier-type"),code=Code("localVn"))]),system=Uri(f"https://terms.sil-th.org/hcode/5/{row.hospital_code}/VN"), value=String(matched.row_3opd.sequence))]
                account.subject = [Reference(reference=patient.relative_path())]
                account.servicePeriod = Period(start=matched.row_3opd.dateopd+matched.row_3opd.timeopd)
                account.extension = [Extension(url=Uri("https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-account-coverage-use"), valueCodeableConcept=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-43plus-coverage-use"), code=Code(matched.row_3opd.uuc))]))]
                account.id = Id(f"cid-{row.citizen_id}-vn-{matched.row_3opd.sequence}")

                # Encounter
                encounter = Encounter.construct()
                encounter.status = Code("finished")
                encounter.identifier = [Identifier(type=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-identifier-type"),code=Code("localVn"))]),system=Uri(f"https://terms.sil-th.org/hcode/5/{row.hospital_code}/VN"), value=String(matched.row_3opd.sequence))]
                encounter.class_fhir = Coding(system=Uri("http://terminology.hl7.org/CodeSystem/v3-ActCode"), code=Code("AMB"), display=String("ambulatory"))
                encounter.subject = Reference(reference=patient.relative_path())
                encounter.period = Period(start=matched.row_3opd.dateopd+matched.row_3opd.timeopd)
                if isinstance(matched.row_1ins.htype,str):
                    encounter.serviceProvider = Reference(reference=matched_org.relative_path(),
                                                          extension=[Extension(url=Uri("https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-encounter-provider-type"), valueCodeableConcept=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-eclaim-provider-type"), code=Code(matched.row_1ins.htype), display=String("Main Contractor"))]))])
                else:
                    encounter.serviceProvider = Reference(reference=matched_org.relative_path())
                encounter.account = [Reference(reference=account.relative_path())]
                #encounter.diagnosis = [EncounterDiagnosis(condition=Reference(display=String(matched.row_3opd.icd10)))]
                #encounter.hospitalization = EncounterHospitalization(admitSource=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-eclaim-admit-source"), code=Code(matched.row_3opd.admit_source))]))
                encounter.location = [EncounterLocation(location=Reference(identifier=Identifier(system=Uri(f"https://terms.sil-th.org/hcode/5/{row.hospital_code}/DepCode"), value=String(matched.row_3opd.clinic))))]
                encounter.extension = [Extension(url=Uri("https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-encounter-service-type-th"), valueCodeableConcept=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-eclaim-service-type-th"), code=Code(matched.row_3opd.optype), display=String("OP บัตรตัวเอง"))]))]
                encounter.id = Id(f"cid-{row.citizen_id}-vn-{matched.row_3opd.sequence}")

                # ServiceRequest
                if matched.row_4orf is not None:
                    service_request = ServiceRequest.construct()
                    service_request.status = Code("completed")
                    service_request.intent = Code("order")
                    service_request.code = CodeableConcept(coding=[Coding(system=Uri("http://snomed.info/sct"), code=Code("3457005"), display=String("Patient referral"))])
                    service_request.subject = Reference(reference=patient.relative_path())
                    service_request.encounter = Reference(reference=encounter.relative_path())
                    service_request.performer = [Reference(reference=matched_org.relative_path())]
                    service_request.id = Id(f"cid-{row.citizen_id}-vn-{matched.row_3opd.sequence}-sr")
                service_request.code = CodeableConcept(coding=[Coding(system=Uri("http://snomed.info/sct"), code=Code("3457005"), display=String("Patient referral"))])

                # Condition

                # Procedure

                # Claim (11,12)
                if matched.row_1ins is not None and matched.row_12cha is not None:
                    claim = Claim.construct()
                    claim.status = Code("active")
                    claim.extension = [
                        Extension(url=Uri("https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-claim-total-cost"), valueMoney=Money(value=Decimal(100), currency=Code("THB"))),
                        Extension(url=Uri("https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-claim-total-copay"), valueMoney=Money(value=Decimal(100), currency=Code("THB"))),
                        Extension(url=Uri("https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-claim-total-paid"), valueMoney=Money(value=Decimal(matched.row_11cht.paid), currency=Code("THB"))),
                    ]
                    #claim.identifier = [
                    #    Identifier(type=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-identifier-type"),code=Code("localVn"))]),system=Uri(f"https://terms.sil-th.org/hcode/5/{row.hospital_code}/Inv"), value=String(matched.row_11cht.invno)),
                    #    Identifier(type=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-identifier-type"),code=Code("localVn"))]),system=Uri(f"https://terms.sil-th.org/hcode/5/{row.hospital_code}/Inv"), value=String(matched.row_11cht.invoice_lt)),
                    #]
                    claim.type = CodeableConcept(c0oding=[Coding(system=Uri("http://terminology.hl7.org/CodeSystem/claim-type"), code=Code("institutional"))])
                    claim.use = Code("claim")
                    claim.patient = Reference(reference=patient.relative_path())
                    claim.created = String(matched.row_11cht.invdate)
                    claim.provider = Reference(reference=matched_org.relative_path())
                    claim.priority = CodeableConcept(coding=[Coding(system=Uri("http://terminology.hl7.org/CodeSystem/processpriority"), code=Code("normal"))])
                    #claim.supportingInfo = [ClaimSupportingInfo(sequence=1, )]
                    claim.insurance = [ClaimInsurance(sequence=1, focal=Boolean(True), coverage=Reference(reference=coverage.relative_path()))]
                    claim.total = Money(value=Decimal(matched.row_11cht.total), currency=Code("THB"))
                    claim.item = [ClaimItem()]
                    claim.id = Id(f"cid-{row.citizen_id}-vn-{matched.row_3opd.sequence}-claim")
                if matched.row_16dru is not None:
                    # Claim (16)
                    drug_claim = Claim.construct()
                    drug_claim.status = Code("active")
                    drug_claim.type = CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-identifier-type"), code=Code("localInvNo"), display=String("เลขที่อ้างอิงใบแจ้งหนี้ของหน่วยบริการ"))])
                    drug_claim.use = Code("claim")
                    drug_claim.patient = Reference(reference=patient.relative_path())
                    drug_claim.created = String(matched.row_16dru.service_date)
                    drug_claim.provider = Reference(reference=matched_org.relative_path())
                    drug_claim.priority = CodeableConcept(coding=[Coding(system=Uri("http://terminology.hl7.org/CodeSystem/processpriority"), code=Code("normal"))])
                    if coverage is not None:
                        drug_claim.insurance = [ClaimInsurance(sequence=1,focal=Boolean(True), coverage=Reference(reference=coverage.relative_path()),preAuthRef=[String(matched.row_16dru.pa_no)])]
                    drug_claim.total = Money(value=Decimal(matched.row_16dru.total_amount), currency=Code("THB"))
                    drug_claim.item = [ClaimItem(sequence=1, productOrService=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-local-drug-code"), code=Code(matched.row_16dru.drug_id)),Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-24drug"), code=Code(matched.row_16dru.drug_id24))], text=String(matched.row_16dru.drug_name)), quantity=Quantity(value=Decimal(matched.row_16dru.amount), unit=String(matched.row_16dru.unit)),serviceDate=String(matched.row_16dru.service_date), encounter=Reference(reference=encounter.relative_path()) ,unitPrice=Money(value=Decimal(matched.row_16dru.drug_price), currency=Code("THB")), net=Money(value=Decimal(matched.row_16dru.total), currency=Code("THB")))]
                    drug_claim.id = Id(f"cid-{row.citizen_id}-vn-{matched.row_3opd.sequence}-24-{matched.row_16dru.drug_id24}")
                    # MedicationDispense
                    medication_dispense = MedicationDispense.construct()
                    medication_dispense.status = Code("completed")
                    medication_dispense.medicationCodeableConcept = CodeableConcept(text=String(matched.row_16dru.drug_name), coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-local-drug-code"), code=Code(matched.row_16dru.drug_id)),Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-24drug"), code=Code(matched.row_16dru.drug_id24))])
                    medication_dispense.subject = Reference(reference=patient.relative_path())
                    medication_dispense.context = Reference(reference=encounter.relative_path())
                    medication_dispense.performer = [MedicationDispensePerformerType(function=CodeableConcept(coding=[Coding(system=Uri("http://terminology.hl7.org/CodeSystem/medicationdispense-performer-function"), code=Code("finalchecker"))], actor=Reference(type=String("Practitioner"), identifier=Identifier(system=String("https://terms.sil-th.org/id/th-pharmacist-id"),value=String(matched.row_16dru.doctor_id)))))]
                    medication_dispense.quantity = Quantity(value=Decimal(matched.row_16dru.amount), unit=String(matched.row_16dru.unit))
                    medication_dispense.whenHandedOver = String(matched.row_16dru.service_date)
                    medication_dispense.id = Id(f"cid-{row.citizen_id}-vn-{matched.row_3opd.sequence}-24-{matched.row_16dru.drug_id24}-md")
                    # MedicationRequest
                    medication_request = MedicationRequest.construct()
                    medication_request.status = Code("completed")
                    medication_request.extension = [Extension(url=Uri("https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-medicationrequest-med-approved-no"), valueString=String(matched.row_16dru.pa_no))]
                    if(isinstance(matched.row_16dru.drug_remark,str)):
                        medication_request.extension.append(Extension(url=Uri("https://fhir-ig.sil-th.org/mophpc/StructureDefinition/ex-medicationrequest-ned-criteria"), valueCodeableConcept=CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-eclaim-medication-ned-criteria"), code=Code(matched.row_16dru.drug_remark), display=String("เกิดอาการไม่พึงประสงค์จากยาหรือแพ้ยาที่สามารถใช้ได้ในบัญชียาหลักแห่งชาติ") )])))
                    medication_request.category = CodeableConcept(coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-eclaim-medication-category"), code=Code(matched.row_16dru.use_status), display=String("ใช้ในโรงพยาบาล"))])
                    medication_request.medicationCodeableConcept = CodeableConcept(text=String(matched.row_16dru.drug_name), coding=[Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-local-drug-code"), code=Code(matched.row_16dru.drug_id)),Coding(system=Uri("https://terms.sil-th.org/CodeSystem/cs-th-24drug"), code=Code(matched.row_16dru.drug_id24))])
                    medication_request.subject = Reference(reference=patient.relative_path())
                    medication_request.encounter = Reference(reference=encounter.relative_path())
                    medication_request.authoredOn = String(matched.row_16dru.service_date)
                    medication_request.id = Id(f"cid-{row.citizen_id}-vn-{matched.row_3opd.sequence}-24-{matched.row_16dru.drug_id24}-mr")
            break

    #bundle_cycler(patients_dict.values(), processed_results)

    return processed_results
