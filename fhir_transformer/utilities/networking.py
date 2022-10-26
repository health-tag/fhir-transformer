import warnings

import jsonpickle

from fhir_transformer.models.result import BundleResult, EntryResult
import requests
import traceback
import re

from fhir_transformer.FHIR.Bundle import Bundle
from fhir_transformer.fhir_transformer_config import base_fhir_url
from fhir_transformer.fhir_transformer_config import headers

actual_header = {
    **headers,
    "Content-Type": "application/json"
}


def post_bundle_to_fhir_server(bundle: Bundle) -> BundleResult:
    payload = jsonpickle.encode(bundle, unpicklable=False)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            res = requests.post(base_fhir_url, data=payload, headers=actual_header, verify=False)
            fhir_response = res.json()
            if fhir_response["resourceType"] == "OperationOutcome":
                print("SEND")
                print(payload)
                print("RESPONSE")
                print(fhir_response)
                return BundleResult(1000,
                                    [EntryResult(entry.resource.resourceType, entry.fullUrl, "Failure to send") for entry in
                                     bundle.entry])
            results = [EntryResult(entry.resource.resourceType, entry.fullUrl) for entry in bundle.entry]
            for i, entry in enumerate(fhir_response["entry"]):
                results[i].status = entry["response"]["status"]
                results[i].location = entry["response"]["location"] if "location" in entry["response"] else None
                if int(re.sub("[^0-9]", "", results[i].status)) >= 400:
                    results[i].error_fhir_response = entry

            return BundleResult(res.status_code, results)
        except Exception:
            traceback.print_exc()
            return BundleResult(1000,
                                [EntryResult(entry.resource.resourceType, entry.fullUrl, "Failure to send") for entry in
                                 bundle.entry])
