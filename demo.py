import math
from datetime import datetime

from fhir_transformer.FHIR.Bundle import BundleType, Bundle
from fhir_transformer.FHIR.Encounter import EncounterDispensing, EncounterDispensingBuilder
from fhir_transformer.FHIR.Location import Location
from fhir_transformer.FHIR.MedicationDispense import MedicationDispense, MedicationDispenseBuilder
from fhir_transformer.FHIR.Organization import Organization
from fhir_transformer.FHIR.Patient import Patient, PatientBuilder
from fhir_transformer.FHIR.Practitioner import Practitioner
from fhir_transformer.models.result import BundleResult
from fhir_transformer.utilities.networking import post_bundle_to_fhir_server
from fhir_transformer.utilities.processing import send_singletype_bundle, bundle_cycler

hospital_blockchain_address = "bx123456789"
hospital_name = "Test"
hospital_code = "5786"
license_id = "ว54321"
doctor = Practitioner(license_id=license_id)
station = "12"
results = list[BundleResult]()
start = datetime.now()

organization = Organization(hospital_name, hospital_blockchain_address,
                            hospital_code)
location = Location(station=station, hospital_blockchain_address=hospital_blockchain_address)
practitioner = Location(station=station, hospital_blockchain_address=hospital_blockchain_address)
send_singletype_bundle([organization], results)
send_singletype_bundle([location], results)
send_singletype_bundle([practitioner], results)

patients: dict[str, Patient] = dict()
encounters: dict[str, list[EncounterDispensing]] = dict()
medicationDispenses: dict[str, list[MedicationDispense]] = dict()

pt_builder = PatientBuilder()
ed_builder = EncounterDispensingBuilder()
md_builder = MedicationDispenseBuilder()

print(f"PREPARE PRACTITIONERS + PATIENT + ENCOUNTER + MEDICAL DISPENSING {datetime.now()}")

for pid in range(1, 1000):
    patient = pt_builder.from_raw(F"{pid}", f"n{pid}", f"s{pid}").add_general_practitioner_organization_ref(
        organization).set_managing_organization_ref(organization).product
    patients[pid] = patient
    encounters[pid] = list()
    medicationDispenses[pid] = list()
    for end in range(1, 11):
        pd = "2022-01-01"
        dd = "2022-01-03"
        encounter = ed_builder.from_raw(f"disp_id{end}", pd, dd, "1").set_patient_ref(patient).set_serviceProvider_ref(
            organization).add_participant_ref(practitioner).product
        encounters[pid].append(encounter)
        for d in range(1, 11):
            medicationDispense = md_builder.from_raw(f"disp_id{end}", "1", f"drug{d}", f"ldrug{d}", "MG", "1234", "10",
                                                     "10", "Eat it", "347", dd).set_patient_ref(
                patient).set_encounter_ref(encounter).add_performer_ref(practitioner).add_performer_ref(
                organization).product
            medicationDispenses[pid].append(medicationDispense)
max_patient_per_cycle = 200
cycle = 0
cycle_entries = list()
patients_count = len(patients.keys())
mode = 1
if mode == 1:
    bundle_cycler(patients.values(), results)
    bundle_cycler([entry for e in encounters.values() for entry in e], results)
    bundle_cycler([entry for e in medicationDispenses.values() for entry in e], results)
    end = datetime.now()
    print(end - start)
    for r in results:
        if r.statusCode >=400:
            print("Error")
if mode == 2:
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
            print(f"{len(cycle_entries)} entries")
            send_bundle(Bundle(BundleType.Transaction, cycle_entries))
            cycle = cycle + 1
            cycle_entries.clear()
print(f"DONE {datetime.now()}")
