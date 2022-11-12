from fhir_transformer.FHIR.Encounter import EncounterDispensing, EncounterDispensingBuilder
from fhir_transformer.FHIR.Location import Location
from fhir_transformer.FHIR.MedicationDispense import MedicationDispense, MedicationDispenseBuilder
from fhir_transformer.FHIR.Organization import Organization
from fhir_transformer.FHIR.Patient import Patient, PatientBuilder
from fhir_transformer.FHIR.Practitioner import Practitioner
from fhir_transformer.csop.files.billdisp import open_bill_disp_xml
from fhir_transformer.csop.files.billtrans import open_bill_trans_xml
from fhir_transformer.fhir_transformer_config import hospital_blockchain_address
from fhir_transformer.models.result import BundleResult
from fhir_transformer.utilities.processing import send_singletype_bundle, bundle_cycler


def process(processed_results: list[BundleResult], bill_trans_xml_path: str, bill_disp_xml_path: str) -> list[
    BundleResult]:
    bill_trans_xml = open_bill_trans_xml(bill_trans_xml_path)
    bill_disp_xml = open_bill_disp_xml(bill_disp_xml_path)

    organization = Organization(bill_trans_xml.hospital_name, hospital_blockchain_address,
                                bill_trans_xml.hospital_code)
    send_singletype_bundle([organization], processed_results)

    locations = dict()
    for inv_no, bill_trans_item in bill_trans_xml.bill_trans_items_dict.items():
        locations[bill_trans_item.station] = Location(station=bill_trans_item.station,
                                                      hospital_blockchain_address=hospital_blockchain_address)
    send_singletype_bundle(locations.values(), processed_results)

    patient_builder = PatientBuilder()
    practitioners = dict[str, Practitioner]()
    patients = dict[str, Patient]()
    encounters: dict[str, list[EncounterDispensing]] = dict()
    medicationDispenses: dict[str, list[MedicationDispense]] = dict()
    encounter_builder = EncounterDispensingBuilder()
    medication_dispense_builder = MedicationDispenseBuilder()
    for disp_id, bill_disp_item in bill_disp_xml.items():
        matched_bill_trans_item = bill_trans_xml.bill_trans_items_dict[bill_disp_item.inv_no]

        if bill_disp_item.license_id not in practitioners.keys():
            practitioners[bill_disp_item.license_id] = practitioner = Practitioner(
                license_id=bill_disp_item.license_id)
        else:
            practitioner = practitioners[bill_disp_item.license_id]

        if matched_bill_trans_item.pid not in patients.keys():
            patients[matched_bill_trans_item.pid] = patient = patient_builder.from_csop(matched_bill_trans_item) \
                .set_managing_organization_ref(organization) \
                .add_general_practitioner_organization_ref(organization) \
                .product
        else:
            patient = patients[matched_bill_trans_item.pid]

        encounters[matched_bill_trans_item.pid] = list()
        medicationDispenses[matched_bill_trans_item.pid] = list()

        encounter = encounter_builder.from_csop(bill_disp_item) \
            .set_patient_ref(patient) \
            .add_participant_ref(practitioners[bill_disp_item.license_id]) \
            .set_serviceProvider_ref(organization) \
            .product
        encounters[matched_bill_trans_item.pid].append(encounter)
        for bill_disp_item_detail in bill_disp_item.details:
            # bill_disp_item -> encounter and bill_disp_item.details -> medicationDispense is already matched in open_bill_disp_xml()
            medication_dispense = medication_dispense_builder.from_csop(bill_disp_item, bill_disp_item_detail) \
                .set_patient_ref(patient) \
                .set_encounter_ref(encounter) \
                .add_performer_ref(practitioner) \
                .add_performer_ref(organization) \
                .product
            medicationDispenses[matched_bill_trans_item.pid].append(medication_dispense)
    send_singletype_bundle(practitioners.values(), processed_results)
    # PREPARE PATIENT + ENCOUNTER + MEDICATION DISPENSE
    bundle_cycler(patients.values(), processed_results)
    bundle_cycler([entry for e in encounters.values() for entry in e], processed_results)
    bundle_cycler([entry for e in medicationDispenses.values() for entry in e], processed_results)
    return
    '''
    cycle = 0
    cycle_entries = list[Entry]()
    patients_count = len(patients.keys())
    print(
        f"SENDING PATIENT + ENCOUNTER + MEDICAL DISPENSING IN {math.ceil(patients_count / max_patient_per_cycle)} CYCLES {datetime.now()}")
    for i, key in enumerate(patients.keys()):
        cycle_entries = cycle_entries + [patients[key].create_entry()]
        if key in encounters:
            cycle_entries = cycle_entries + [encounter.create_entry() for encounter in encounters[key]]
        if key in medicationDispenses:
            cycle_entries = cycle_entries + [medication_dispense.create_entry() for medication_dispense in
                                             medicationDispenses[key]]
        if ((i > 0) and (i % max_patient_per_cycle == 0)) or (i + 1 == patients_count):
            print(f"SENDING PATIENT + ENCOUNTER + MEDICAL DISPENSING CYCLE {cycle + 1} {datetime.now()}")
            send_bundle(Bundle(BundleType.Transaction, cycle_entries))
            cycle = cycle + 1
            cycle_entries.clear()
    '''
