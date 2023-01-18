import os
import uuid
import zipfile
from datetime import datetime
from pathlib import Path, PurePath

import jsonpickle
from watchdog.events import FileSystemEventHandler, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED
from watchdog.observers.polling import PollingObserver

from fhir_transformer.csop.processor import process
from fhir_transformer.eclaims.processor import process_all as eclaims_process
from fhir_transformer.utilities.logging import Tee, Guard


def checkfiles_in_folder(folder_path: Path):
    print(f"-> {folder_path}")
    csop_checklist = dict[str, bool]()
    csop_checklist["billdisp"] = False
    csop_checklist["billtran"] = False

    elaims_checklist = dict[str, bool]()
    elaims_checklist["ins"] = False
    elaims_checklist["pat"] = False
    elaims_checklist["opd"] = False
    elaims_checklist["orf"] = False
    elaims_checklist["odx"] = False
    elaims_checklist["oop"] = False
    elaims_checklist["cht"] = False
    elaims_checklist["dru"] = False

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
        for key, value in iter(elaims_checklist.items()):
            if key in file.name.lower():
                elaims_checklist[key] = True

    is_csop = all(csop_checklist.values()) and not is_done
    is_folders43 = all(folders43_checklist.values()) and not is_done
    is_eclaims = all(elaims_checklist.values()) and not is_done
    if is_csop:
        print(f"{folder_path} will be processed as CSOP.")
        return "csop"
    elif is_folders43:
        print(f"{folder_path} will be processed as 43 Folders.")
        return "folders43"
    elif is_eclaims:
        print(f"{folder_path} will be processed as E-Claims Folders.")
        return "eclaims"
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


def run_eclaims_folder(folder_path: Path):
    directory = folder_path.resolve()
    with Tee(f"{directory}/log.txt", jobId=directory.name):
        with Guard(directory) as results:
            print(f"Converting Eclaim Files in {folder_path.absolute()}")
            files = list(folder_path.glob("*"))
            if len(files) == 0:
                print(f"No file found!")
            else:
                print(f"{len(files)} file found")
                for file in files:
                    print(file)
            _1ins_path: Path | None = None
            _2pat_path: Path | None = None
            _3opd_path: Path | None = None
            _4orf_path: Path | None = None
            _5odx_path: Path | None = None
            _6oop_path: Path | None = None
            _11cht_path: Path | None = None
            _16dru_path: Path | None = None
            for file in files:
                if "ins" in file.name.lower():
                    _1ins_path = file
                if "pat" in file.name.lower():
                    _2pat_path = file
                if "opd" in file.name.lower():
                    _3opd_path = file
                if "orf" in file.name.lower():
                    _4orf_path = file
                if "odx" in file.name.lower():
                    _5odx_path = file
                if "oop" in file.name.lower():
                    _6oop_path = file
                if "cht" in file.name.lower():
                    _11cht_path = file
                if "dru" in file.name.lower():
                    _16dru_path = file

            if _1ins_path is None or _2pat_path is None or _3opd_path is None or _4orf_path is None or _5odx_path is None or _6oop_path is None or _11cht_path is None or _16dru_path is None:
                print("Requires all of ins pat opd orf odx oop cht dru files")
                return
            print(f"Processing {_1ins_path.name} {_2pat_path.name} {_3opd_path.name} {_4orf_path.name} {_5odx_path.name} {_6oop_path.name} {_11cht_path.name} {_16dru_path.name}")
            eclaims_process(results,_1ins_path=str(_1ins_path), _2pat_path=str(_2pat_path), _3opd_path=str(_3opd_path), _4orf_path=str(_4orf_path), _5odx_path=str(_5odx_path), _6oop_path=str(_6oop_path), _11cht_path=str(_11cht_path), _16dru_path=str(_16dru_path))
            return