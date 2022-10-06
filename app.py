from collections import deque
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass
from typing import Optional
import requests

from flask import Flask, make_response
import subprocess
import sys

base_node_url = "http://backend:3000/api"

@dataclass
class Job:
    id: str
    status: str
    future: Optional[Future] = None


app = Flask(__name__)

jobs = deque[Job]()

futures = dict[str, Job]()

executor = ThreadPoolExecutor(max_workers=1)


@app.route('/api/queue/<id>', methods=['GET'])
def queue_task(id: str):
    jobs.append(Job(id, "queue"))
    print(f"queue {id}")
    return make_response("A task has been queue", 200)


def run_task(job: Job):
    print(f"Working on {job.id}")
    working_dir = f"./workingdir/uploads/{job.id}"
    with open(f"{working_dir}/log.txt", "wb+") as f:
        child = subprocess.Popen([sys.executable,"-u", f"fhir_transformer/__main__.py", "--type", "csop", "--name", job.id],
                                 cwd="./",
                                 stdout=f, stderr=f, )
        out, err = child.communicate()
        job.status = "finish" if child.returncode == 0 else "error"
        res = requests.get(f"{base_node_url}/job/{job.id}/finish")
        print(res.status_code)


@app.route('/api/start', methods=['GET'])
def run_queue():
    stop_queue()
    futures.clear()
    length = len(jobs)
    print("Start queue")
    for i in range(0, length):
        job = jobs.popleft()
        f = executor.submit(run_task(job))
        job.future = f
        futures[job.id] = job
    return make_response("A queue is started.", 200)


@app.route('/api/stop', methods=['GET'])
def stop_queue():
    print("Stop queue")
    jobs_list = list(enumerate(futures.values()))
    for job in jobs_list:
        try:
            job.future.cancel()
        except:
            pass
    return make_response("A queue is stopped.", 200)


if __name__ == '__main__':
    print("FHIR TRANSFORMER FLASK WEBAPI")
    app.run(host='0.0.0.0', port=105)
