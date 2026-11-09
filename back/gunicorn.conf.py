import os
import shutil

from prometheus_client import multiprocess

MULTIPROC_DIR = os.environ.get("PROMETHEUS_MULTIPROC_DIR")


def on_starting(server):
    if MULTIPROC_DIR:
        shutil.rmtree(MULTIPROC_DIR, ignore_errors=True)
        os.makedirs(MULTIPROC_DIR)


def child_exit(server, worker):
    if MULTIPROC_DIR:
        multiprocess.mark_process_dead(worker.pid)
