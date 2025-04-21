from jobs import get_job_by_id, update_job_status, q, rd, rdb
import json
import logging
from datetime import datetime
import socket
import os

# Logging setup
loglevel = os.environ.get('LOG_LEVEL', 'INFO').upper()
format_str = f'[%(asctime)s {socket.gethostname()}] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
logging.basicConfig(level=loglevel, format=format_str)

def bin_magnitude(mag):
    """Convert a magnitude float into a labeled bin (e.g., '3.0–3.9')"""
    if mag is None:
        return "unknown"
    try:
        lower = int(mag)
        upper = lower + 0.9
        return f"{lower}.0–{upper:.1f}"
    except:
        return "invalid"

@q.worker
def do_work(jobid):
    """
    Worker to compute frequency of earthquakes in magnitude bins for a given job.
    Assumes job contains filtering logic if needed (e.g., region/type).
    """
    logging.info(f"[Worker] Starting job: {jobid}")
    update_job_status(jobid, 'in progress')

    job = get_job_by_id(jobid)

    # Placeholder: if your job includes filters, extract them here
    # For now, use all data in Redis DB 0

    result = {}
    for key in rd.keys():
        try:
            quake = json.loads(rd.get(key))
            mag = quake.get("properties", {}).get("mag")
            bin_label = bin_magnitude(mag)
            result[bin_label] = result.get(bin_label, 0) + 1
        except Exception as e:
            logging.warning(f"Failed to process record {key}: {e}")

    rdb.set(jobid, json.dumps(result))
    update_job_status(jobid, 'complete')
    logging.info(f"[Worker] Job {jobid} completed. Binned {sum(result.values())} earthquakes.")

