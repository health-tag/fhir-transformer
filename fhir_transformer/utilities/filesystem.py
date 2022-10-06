from pathlib import Path

import jsonpickle
from watchdog.events import FileSystemEventHandler, EVENT_TYPE_DELETED
from watchdog.observers import Observer

from fhir_transformer.csop.processor import process


def checkfiles_in_folder(folder_path: Path):
    csop_checklist = dict[str, bool]()
    csop_checklist["billdisp"] = False
    csop_checklist["billtrans"] = False

    folders43_checklist = dict[str, bool]()
    folders43_checklist["person"] = False
    folders43_checklist["provider"] = False
    folders43_checklist["drug_opd"] = False

    files = Path(folder_path).glob("./*")
    is_done = False
    for file in files:
        lower_name = file.name.lower()
        if "done" in lower_name:
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
        return "csop"
    elif is_folders43:
        return "folders43"
    else:
        return None


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
        self.observer = Observer()
        self.watchDirectory = directory

    def start(self):
        self.observer = Observer()
        event_handler = Handler()
        self.observer.schedule(event_handler, str(self.watchDirectory), recursive=True)
        self.observer.start()
        print(f'Watching {self.watchDirectory} folder for any changes')

    def stop(self):
        self.observer.stop()
        self.observer.join()


def run_csop_folder(folder_path: Path):
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
    print(f"PROCESSING {bill_trans_xml_path.name} AND {bill_disp_xml_path.name}")
    result = process(bill_trans_xml_path=str(bill_trans_xml_path),
                     bill_disp_xml_path=str(bill_disp_xml_path))
    directory = folder_path.resolve()
    print("DONE")
    with open(f"{directory}/result.json", "w") as out_file:
        out_file.write(jsonpickle.encode(result, unpicklable=False, indent=True))
    if all([r.statusCode < 400 for r in result]):
        with open(f"{directory}/done", "w"):
            pass
    else:
        with open(f"{directory}/error", "w"):
            pass
    return
