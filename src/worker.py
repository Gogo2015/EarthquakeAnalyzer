import json
import time
import logging
import os
from jobs import q, update_job_status, get_job_by_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@q.worker
def worker(jobid):
    # Get the job details
    job = get_job_by_id(jobid)
    
    if not job:
        logger.error(f"Job {jobid} not found")
        return
    
    logger.info(f"Processing job {jobid}")
    
    # Update status to 'in progress'
    update_job_status(jobid, "in progress")

    # delay for 5 seconds
    time.sleep(5)
    
    # Update job status to complete
    update_job_status(jobid, "complete")
    logger.info(f"Completed job {jobid}")

if __name__ == "__main__":
    # Start the worker
    logger.info("Starting worker...")
    worker()