import traceback
import sys
import os
import jsonpickle

from fhir_transformer.models.result import BundleResult


# Context manager that copies stdout and any exceptions to a log file
class Tee(object):
    def __init__(self, filename):
        self.file = open(filename, 'w', encoding="utf-8")
        self.stdout = sys.stdout

    def __enter__(self):
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, tb):
        sys.stdout = self.stdout
        if exc_type is not None:
            self.file.write(traceback.format_exc())
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

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
