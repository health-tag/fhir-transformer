import os
import uuid
import zipfile
from datetime import datetime
from pathlib import Path, PurePath

import jsonpickle
from watchdog.events import FileSystemEventHandler, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED
from watchdog.observers.polling import PollingObserver

from fhir_transformer.csop.processor import process
from fhir_transformer.utilities.logging import Tee, Guard


def checkfiles_in_folder(folder_path: Path):
    print(f"-> {folder_path}")
    csop_checklist = dict[str, bool]()
    csop_checklist["billdisp"] = False
    csop_checklist["billtran"] = False

    folders43_checklist = dict[str, bool]()
    folders43_checklist["person"] = False
    folders43_checklist["provider"] = False
    folders43_checklist["drug_opd"] = False
    files = Path(folder_path).glob("*")
    is_done = False
    for file in files:
        lower_name = file.name.lower()
        if "done" in lower_name:
            is_done = True
        if "error" in lower_name:
            is_done = True
        if "working" in lower_name:
            is_done = True
        for key, value in iter(csop_checklist.items()):
            if key in lower_name:
                csop_checklist[key] = True
        for key, value in iter(folders43_checklist.items()):
            if key in file.name.lower():
                folders43_checklist[key] = True

    is_csop = all(csop_checklist.values()) and not is_done
    is_folders43 = all(folders43_checklist.values()) and not is_done
    if is_csop:
        print(f"{folder_path} will be processed as CSOP.")
        return "csop"
    elif is_folders43:
        print(f"{folder_path} will be processed as 43 Folders.")
        return "folders43"
    else:
        return None

def findWorkingFolder(path:PurePath,iteration=0):
    if(iteration > 10):
        return False
    else:
        parent = path.parent
        if(parent.name.lower()=="workingdir"):
            return parent
        else:
            return findWorkingFolder(parent, iteration+1)


class Handler(FileSystemEventHandler):
    pendingJob = dict[str, bool]()

    @staticmethod
    def on_any_event(event):
        source_path = Path(event.src_path)
        if event.is_directory:
            return
        if event.event_type == EVENT_TYPE_DELETED and not (
                source_path.name.lower() == "done" or source_path.name.lower() == "error"):
            return
        if ("csop_zips" in str(source_path).lower()) and (event.event_type == EVENT_TYPE_CREATED) and (".zip" in source_path.suffix.lower()):
            with zipfile.ZipFile(source_path, 'r') as zip_ref:
                id = str(uuid.uuid4())
                workingdir = findWorkingFolder(source_path)
                if workingdir is not False:
                    zip_folder = workingdir / "uploads" / id
                    zip_ref.extractall(zip_folder)
                    files = zip_folder.glob("*")
                    meta = {"id": id, "description": f"Automatically created from {source_path.name}",
                            "files": [f.name for f in files],
                            "type": "csop", "dataDate": datetime.now(), "taskDate": datetime.now()}
                    with open(zip_folder / "info.json", "w") as info_file:
                        info_file.write(jsonpickle.encode(meta, unpicklable=False, indent=True))
                    with open(zip_folder / "csop", "w") as task_file:
                        task_file.write("")
            os.remove(source_path)
            return
        job_folder_path = source_path.parent
        if job_folder_path.name not in Handler.pendingJob or ~Handler.pendingJob[job_folder_path.name]:
            result = checkfiles_in_folder(job_folder_path)
            match result:
                case "csop":
                    Handler.pendingJob[job_folder_path.name] = True
                    run_csop_folder(job_folder_path)
                    Handler.pendingJob[job_folder_path.name] = False


class WorkingDirWatcher:
    def __init__(self, directory: Path):
        self.observer = PollingObserver()
        self.watchDirectory = directory

    def start(self):
        self.observer = PollingObserver()
        event_handler = Handler()
        self.observer.schedule(event_handler, str(self.watchDirectory), recursive=True)
        self.observer.start()
        print(f'Watching {self.watchDirectory} folder for any changes')

    def stop(self):
        self.observer.stop()
        self.observer.join()


def run_csop_folder(folder_path: Path):
    directory = folder_path.resolve()
    with Tee(f"{directory}/log.txt", jobId=directory.name):
        with Guard(directory) as results:
            print(f"Converting CSOP Files in {folder_path.absolute()}")
            files = list(folder_path.glob("*"))
            if len(files) == 0:
                print(f"No file found!")
            else:
                print(f"{len(files)} file found")
                for file in files:
                    print(file)
            bill_trans_xml_path: Path | None = None
            bill_disp_xml_path: Path | None = None
            for file in files:
                if "billtran" in file.name.lower():
                    bill_trans_xml_path = file
                if "billdisp" in file.name.lower():
                    bill_disp_xml_path = file
            if bill_trans_xml_path is None or bill_disp_xml_path is None:
                print("Requires both of BILLTRANS and BILLDISP files")
                return
            print(f"Processing {bill_trans_xml_path.name} AND {bill_disp_xml_path.name}")
            process(processed_results=results, bill_trans_xml_path=str(bill_trans_xml_path),
                    bill_disp_xml_path=str(bill_disp_xml_path))
            return
