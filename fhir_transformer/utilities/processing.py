from datetime import datetime
from math import ceil
from typing import Iterable

from fhir_transformer.FHIR.Base import FHIRResource
from fhir_transformer.FHIR.Bundle import Bundle, BundleType
from fhir_transformer.FHIR.Entry import Entry
from fhir_transformer.fhir_transformer_config import max_patient_per_cycle
from fhir_transformer.models.result import BundleResult
from fhir_transformer.utilities.networking import post_bundle_to_fhir_server


def send_singletype_bundle(fhir_resources: Iterable[FHIRResource], processed_results: list[BundleResult]):
    resource_name = next(iter(fhir_resources)).resourceType
    print(f"⌚ Convert {resource_name} to FHIR Bundle entries at {datetime.now()} .")
    fhir_resources = [e.create_entry() for e in fhir_resources]
    bundle = Bundle(BundleType.Batch, fhir_resources)
    print(f"Sending {len(fhir_resources)} entries of {resource_name} to FHIR server at {datetime.now()} .")
    processed_results.append(post_bundle_to_fhir_server(bundle))


def bundle_cycler(fhir_resources: Iterable[FHIRResource], processed_results: list[BundleResult]):
    resource_name = next(iter(fhir_resources)).resourceType
    cycle = 0
    cycle_entries = list()
    print(f"⌚ Convert {resource_name} to FHIR Bundle entries at {datetime.now()}")
    entries = [e.create_entry() for e in fhir_resources]
    items_count = len(entries)
    print(f"🔗 There are {items_count} entries which will send in {ceil(items_count / max_patient_per_cycle)} cycle.")
    for i in range(0, items_count):
        cycle_entries.append(entries[i])
        if ((i > 0) and (i % max_patient_per_cycle == 0)) or (i + 1 == items_count):
            print(f"📡 Sending {resource_name} cycle {cycle + 1} of {ceil(items_count / max_patient_per_cycle)} at {datetime.now()}.")
            processed_results.append(post_bundle_to_fhir_server(Bundle(BundleType.Batch, cycle_entries)))
            cycle = cycle + 1
            cycle_entries.clear()
    return
