from datetime import datetime

from fhir_transformer.FHIR.Bundle import Bundle, BundleType
from fhir_transformer.FHIR.Location import Location
from fhir_transformer.FHIR.Organization import Organization
from fhir_transformer.fhir_transformer_config import hospital_name_43folders, hospital_blockchain_address
from fhir_transformer.folders43.csv_extractor import _open_person_csv, _open_provider_csv, _open_drug_opd_csv
from fhir_transformer.models.result import BundleResult
from fhir_transformer.utilities.networking import post_bundle_to_fhir_server


def process(person_csv_path: str, drug_opd_csv_path: str, provider_csv_path: str) -> list[BundleResult]:
    results = list[BundleResult]()
    personCSV = _open_person_csv(person_csv_path)
    drugDict = _open_drug_opd_csv(drug_opd_csv_path)  # pid,DrugItem
    providerDict = _open_provider_csv(provider_csv_path)  # providerId,ProviderItem
    print(f"Prepare ORGANIZATION {datetime.now()}")
    organization_bundle = Bundle(BundleType.Batch,
                                 [Organization(hospital_name_43folders, hospital_blockchain_address,
                                               next(iter(personCSV.values())).hospital_code).create_entry()])
    print(f"Sent ORGANIZATION {datetime.now()}")
    results.append(post_bundle_to_fhir_server(organization_bundle))
    print(f"Prepare LOCATION {datetime.now()}")
    locations = dict()
    for pid, item in drugDict.items():
        locations[item.clinic] = Location(station=item.clinic,
                                                      hospital_blockchain_address=hospital_blockchain_address)
    locations_bundle = Bundle(BundleType.Batch, [entry.create_entry() for entry in list(locations.values())])
    post_bundle_to_fhir_server(locations_bundle)
    print(f"Sent LOCATION {datetime.now()}")

    print(f"Prepare PRACTITIONER {datetime.now()}")
    practitioners_bundle = Bundle(BundleType.Batch, [entry.create_entry() for entry in list(providerDict.items())])
    print(f"Sent PRACTITIONER {datetime.now()}")
    return results
