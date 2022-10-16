import traceback
import sys
import os
import warnings
import httpx
import jsonpickle

from fhir_transformer.fhir_transformer_config import file_uploader_server_url
from fhir_transformer.models.result import BundleResult


# Context manager that copies stdout and any exceptions to a log file
class Tee(object):

    def __init__(self, filename, jobId: str = None):

        if file_uploader_server_url is not None:
            self.client = httpx.AsyncClient()
        self.file = open(filename, 'w', encoding="utf-8")
        self.jobId = jobId
        self.stdout = sys.stdout

    def __enter__(self):
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, tb):
        if file_uploader_server_url is not None:
            self.client.aclose()
        sys.stdout = self.stdout
        if exc_type is not None:
            self.file.write(traceback.format_exc())
            self.send_ending("error")
        else:
            self.send_ending("finish")
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
        self.send_console_line(data)

    def send_ending(self, param: str):
        if self.jobId is not None and file_uploader_server_url is not None:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    self.client.get(f"{file_uploader_server_url}/python/{self.jobId}/{param}")
                except:
                    pass

    def send_console_line(self, data):
        if self.jobId is not None and file_uploader_server_url is not None:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    self.client.post(f"{file_uploader_server_url}/python", json={"jobId": self.jobId, "line": data})
                except:
                    pass

    def flush(self):
        self.file.flush()
        self.stdout.flush()


class Guard(object):

    def __init__(self, directory):
        self.directory = directory
        self.results = list[BundleResult]()

    def __enter__(self):
        if os.path.exists(f"{self.directory}/done"):
            os.remove(f"{self.directory}/done")
        if os.path.exists(f"{self.directory}/error"):
            os.remove(f"{self.directory}/error")
        with open(f"{self.directory}/working", "w"):
            pass
        return self.results

    def __exit__(self, exc_type, exc_value, tb):
        if os.path.exists(f"{self.directory}/working"):
            os.remove(f"{self.directory}/working")
        with open(f"{self.directory}/result.json", "w") as out_file:
            out_file.write(jsonpickle.encode(self.results, unpicklable=False, indent=True))
        if exc_type is not None:
            print("😵 Finish with exceptions. Please check log.txt and result.json")
            with open(f"{self.directory}/error", "w"):
                return
        else:
            if all([r.statusCode < 400 for r in self.results]):
                print("🥰 Finish without any errors")
                with open(f"{self.directory}/done", "w"):
                    return
            else:
                print("😓 Finish with FHIR errors. Please check log.txt and result.json")
                with open(f"{self.directory}/error", "w"):
                    return
