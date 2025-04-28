import pytest
import requests
import time
import json

def test_handle_data_DELETE():
    response = requests.delete('http://127.0.0.1:5000/data')
    assert response.status_code == 200
    assert response.json()['message'] == 'Data deleted successfully'
    assert isinstance(response.json(), dict) == True

def test_handle_data_POST():
    response = requests.post('http://127.0.0.1:5000/data')
    assert response.status_code == 200
    assert response.json()['message'] == 'Data added successfully'
    assert isinstance(response.json(), dict) == True

def test_handle_data_GET():
    response = requests.get('http://127.0.0.1:5000/data')
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True

def test_get_all_earthquakes():
    response = requests.get('http://127.0.0.1:5000/earthquake')
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True

def test_get_specific_earthquake():
    # First fetch an id dynamically
    response = requests.get('http://127.0.0.1:5000/earthquake')
    assert response.status_code == 200
    all_ids = response.json()
    if len(all_ids) > 0:
        earthquake_id = all_ids[0]
        # Now fetch that specific earthquake
        response2 = requests.get(f'http://127.0.0.1:5000/earthquake/{earthquake_id}')
        assert response2.status_code == 200
        assert isinstance(response2.json(), dict) == True

def test_filter_earthquake_by_place():
    response = requests.get('http://127.0.0.1:5000/earthquake?place=tonga')
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True

def test_filter_earthquake_by_magnitude():
    response = requests.get('http://127.0.0.1:5000/earthquake?min_mag=4&max_mag=6')
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True

def test_filter_earthquake_by_date():
    response = requests.get('http://127.0.0.1:5000/earthquake?start=2025-01-01&end=2024-04-01')
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True

def test_submit_jobs_and_get_result():
    data = {"start": "2023-01-01", "end": "2024-01-01"}
    json_data = json.dumps(data)
    response = requests.post("http://127.0.0.1:5000/jobs", 
        data=json_data, 
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    job_id = response.json()['id']
    assert isinstance(response.json(), dict) == True

    # Get specific job info
    response2 = requests.get(f'http://127.0.0.1:5000/jobs/{job_id}')
    assert response2.status_code == 200
    assert isinstance(response2.json(), dict) == True

    # Wait for worker to finish
    time.sleep(8)

    # Fetch results
    response3 = requests.get(f'http://127.0.0.1:5000/results/{job_id}')
    assert response3.status_code == 200
    # Since it returns an image, just check it's not empty
    assert isinstance(response3.content, (bytes, bytearray)) == True

