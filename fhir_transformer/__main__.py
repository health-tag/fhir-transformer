import argparse
import os
import sys
import time
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

import jsonpickle

from fhir_transformer.utilities.filesystem import WorkingDirWatcher, checkfiles_in_folder, run_csop_folder


def banner():
    print("**********************************")
    print("* HealthTAG FHIR Transformer 2.4 *")
    print("*         7 December 2022        *")
    print("*         healthtag.io           *")
    print("*      support@healthtag.io      *")
    print("**********************************")


def watch_folder(folder_path: Path):
    watcher = WorkingDirWatcher(folder_path)
    watcher.start()
    try:
        while True:
            time.sleep(3)
    except KeyboardInterrupt:
        watcher.stop()
        print(f'Stop watching {folder_path} folder')


def check_job_folder(folder_path: Path, iteration = 0):
    sub_paths = list(filter(lambda sp: sp.is_dir, list(folder_path.glob("**"))))
    if len(sub_paths) == 0:
        return
    else:
        if (iteration == 0):
            print(f"Checking on {folder_path} folder for any existing work")
        for sub_path in sub_paths:
            if sub_path.is_dir():
                result = checkfiles_in_folder(sub_path)
                match result:
                    case "csop":
                        run_csop_folder(sub_path)
            elif ("csop_zips" in str(sub_path).lower()) and (sub_path.suffix.lower() == ".zip"):
                with zipfile.ZipFile(sub_path, 'r') as zip_ref:
                    id = str(uuid.uuid4())
                    zip_folder = folder_path / "uploads" / id
                    zip_ref.extractall(zip_folder)
                    files = zip_folder.glob("*")
                    meta = {"id": id, "description": f"Automatically created from {sub_path.name}",
                            "files": [f.name for f in files],
                            "type": "csop", "dataDate": datetime.now(), "taskDate": datetime.now()}
                    with open(zip_folder /"info.json", "w") as info_file:
                        info_file.write(jsonpickle.encode(meta, unpicklable=False, indent=True))
                    with open(zip_folder / "csop", "w") as task_file:
                        task_file.write("")
                os.remove(sub_path)
        if(iteration == 0):
            check_job_folder(folder_path, iteration = 1)
        if (iteration == 1):
            print("Finish running current works")


if __name__ == '__main__':
    banner()
    parser = argparse.ArgumentParser(description='HealthTAG FHIR Transformer')
    parser.add_argument('--watch', dest='watch_mode', action='store_true',
                        help='Use watch mode. Please read the manual to understand how to use this mode')

    parser.add_argument('--type', dest='processing_type', action='store',
                        choices=('csop', '43folders'),
                        help='Specify processing type.')
    parser.add_argument('--name', dest='folder_name', action='store',
                        help='Specify name of folder inside "workingdir" folder')
    args = parser.parse_args()

    if (args.watch_mode is True):
        path = Path("workingdir")
        Path(path).mkdir(exist_ok=True)
        csopzips_path = Path(path / "csop_zips")
        Path(csopzips_path).mkdir(exist_ok=True)
        check_job_folder(path)
        sys.exit(watch_folder(path))

    if (args.processing_type is None or args.folder_name is None):
        print("Please specify --type and --name argument")
        sys.exit(1)
    else:
        if (args.processing_type == "csop"):
            sys.exit(run_csop_folder(Path(f"workingdir/{args.folder_name}")))
        else:
            sys.exit(1)
