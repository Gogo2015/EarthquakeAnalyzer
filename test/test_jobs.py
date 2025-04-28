import pytest
from jobs import add_job, get_job_by_id, update_job_status

def test_add_and_get_job():
    # Arrange
    start_date = "2024-01-01"
    end_date = "2024-12-31"

    # Act
    job = add_job(start_date, end_date)
    job_id = job["id"]
    fetched_job = get_job_by_id(job_id)

    # Assert
    assert fetched_job["start_date"] == start_date
    assert fetched_job["end_date"] == end_date
    assert fetched_job["status"] == "submitted"
    assert fetched_job["id"] == job_id

def test_update_job_status():
    # Arrange
    job = add_job("2024-01-01", "2024-12-31")
    job_id = job["id"]

    # Act
    update_job_status(job_id, "in progress")
    updated_job = get_job_by_id(job_id)

    # Assert
    assert updated_job["status"] == "in progress"

