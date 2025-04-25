# Earthquake Web App

## Project Overview

This project provides a Flask API to access and analyze earthquake data from the United States Geological Survey (USGS). It fetches recent earthquake data, stores it in Redis, and makes it available through a RESTful API. The application features a background job system that leverages Redis queues to process analysis jobs asynchronously, such as hemisphere distribution analysis and magnitude binning.

The entire system is containerized using Docker and can be deployed with Kubernetes for scalability and high availability.

## Help
To view all available routes and their descriptions, visit the `/help` endpoint.

## Database Architecture

Our application uses Redis to efficiently store and manage data:

1. **Raw Data Database (DB 0)**: Stores the earthquake data with earthquake IDs as keys
2. **Queue Database (DB 1)**: Manages the job queue for asynchronous task processing
3. **Jobs Database (DB 2)**: Stores job information including status and parameters
4. **Results Database (DB 3)**: Stores analysis results and generated visualizations

## File Descriptions
```
Earthquake-Web-App/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    ├── diagram.svg
    ├── README.md
    ├── kubernetes
    │   ├── prod
    │   │   ├── app-prod-deployment-flask.yml
    │   │   ├── app-prod-deployment-redis.yml
    │   │   ├── app-prod-deployment-worker.yml
    │   │   ├── app-prod-ingress-flask.yml
    │   │   ├── app-prod-pvc-redis.yml
    │   │   ├── app-prod-service-flask.yml
    │   │   ├── app-prod-service-nodeport-flask.yml
    │   │   └── app-prod-service-redis.yml
    │   └── test
    │       ├── app-test-deployment-flask.yml
    │       ├── app-test-deployment-redis.yml
    │       ├── app-test-deployment-worker.yml
    │       ├── app-test-ingress-flask.yml
    │       ├── app-test-pvc-redis.yml
    │       ├── app-test-service-flask.yml
    │       ├── app-test-service-nodeport-flask.yml
    │       └── app-test-service-redis.yml
    ├── data
    │   └── .gitcanary
    ├── test
    │   └── test_api.py
    └── src
        ├── api.py
        ├── jobs.py
        └── worker.py
```

- [Dockerfile](Dockerfile) - Dockerfile to generate a docker image of our application
- [docker-compose.yml](docker-compose.yml) - Docker-compose file to run the containerized Flask application
- [requirements.txt](requirements.txt) - Required dependencies for the project
- [api.py](./src/api.py) - API endpoints for communication with redis, job management, and data retrieval
- [jobs.py](./src/jobs.py) - Module to handle job requests and queue management
- [worker.py](./src/worker.py) - Worker to process jobs from the queue, generate visualizations, and store results
- [test_api.py](./test/test_api.py) - Integration tests for the Flask application
- [kubernetes/](./kubernetes/) - Configuration files for Kubernetes deployment in test and production environments

## System Architecture

![System Architecture](diagram.svg)

The application consists of three main services:
- **Flask API Service**: Handles HTTP requests, provides data endpoints, manages job creation
- **Redis Database**: Stores earthquake data, job queue, job status, and results (4 separate databases)
- **Worker Service**: Processes jobs from the queue, analyzes earthquake data, generates visualizations, and stores results

## API Endpoints

### Data Endpoints
- `POST /data` - Load earthquake dataset into Redis
- `GET /data` - Return entire earthquake dataset 
- `DELETE /data` - Delete all earthquake data
- `GET /earthquake/all` - Get all earthquake IDs
- `GET /earthquake/<earthquake_id>` - Get specific earthquake data by ID
- `GET /earthquakes/by-place?place=<place>` - Filter earthquakes by place name
- `GET /earthquakes/by-magnitude?min_mag=<min>&max_mag=<max>` - Filter earthquakes by magnitude range
- `GET /earthquakes/by-date?start=<date>&end=<date>` - Filter earthquakes by date range

### Jobs Endpoints
- `POST /jobs` - Create a new job with start and end parameters
- `GET /jobs` - List all job IDs
- `GET /jobs/<job_id>` - Get information about a specific job
- `GET /results/<job_id>` - Get results of a completed job
- `POST /hemisphere-job` - Create a new hemisphere analysis job

## Earthquake Data Overview
The United States Geological Survey (USGS) Earthquake Hazards Program provides access to real-time and historical earthquake data in GeoJSON format through their public API. The dataset includes detailed information about each seismic event, such as its unique ID, magnitude, geographic coordinates (longitude, latitude, depth), timestamp, location description, and status. Additional attributes include the event type, tsunami occurrence flag, magnitude type, and links to more detailed reports. This data can be filtered by time range, magnitude, and geographic bounds via the API. For this project, we download the dataset using a specific API query and store the earthquake records in Redis for efficient access, filtering, and analysis.

## Hemisphere Analysis

The application includes a hemisphere analysis feature that categorizes earthquakes into four hemispheres based on their coordinates:
- Northeast (latitude ≥ 0, longitude ≥ 0)
- Northwest (latitude ≥ 0, longitude < 0)
- Southeast (latitude < 0, longitude ≥ 0)
- Southwest (latitude < 0, longitude < 0)

The hemisphere analysis job filters earthquakes by a minimum magnitude (if specified), counts earthquakes in each hemisphere, calculates statistics for each hemisphere (avg magnitude, max magnitude), and generates a visualization showing the distribution.

## Testing

Test scripts are included in the `test` directory to verify the functionality of the API endpoints, job processing, and worker operations. To run tests:

```
$ pytest
```

## Deployment Instructions

### Local Deployment with Docker

#### Build the image
Navigate to the directory where our Dockerfile, and [docker-compose.yml](docker-compose.yml) are located.

```
$ docker compose build
```

#### Run Flask Application Container
Using the [docker-compose.yml](docker-compose.yml) file we can use it to start the Flask application container:
```
$ docker compose up -d
```
**Note:** -d starts the application in the background

Since we mapped to port 5000 in the [docker-compose.yml](docker-compose.yml) to interact with the Flask endpoints we can use `curl localhost:5000/...`

To stop the container use:
```
$ docker compose down
```

### Kubernetes Deployment

#### Test Environment
Deploy the application to the test environment:

```
$ kubectl apply -f kubernetes/test/
```

#### Production Environment
Deploy the application to the production environment:

```
$ kubectl apply -f kubernetes/prod/
```

#### Accessing the Application
The application will be available at the ingress URL defined in the Kubernetes configuration. To check the URL:

```
$ kubectl get ingress -n <namespace>
```

## Logging Configuration

The application uses Python's logging module. The log level can be configured via the `LOG_LEVEL` environment variable in the docker-compose.yaml file or Kubernetes configuration. Valid log levels are:

- DEBUG
- INFO (default)
- WARNING
- ERROR
- CRITICAL

## Example Usage

### Getting Help
```
$ curl localhost:5000/help
```

### Loading Data
```
$ curl -X POST localhost:5000/data
```

### Viewing All Earthquakes
```
$ curl localhost:5000/data
```

### Getting All Earthquake IDs
```
$ curl localhost:5000/earthquake/all
```

### Filtering Earthquakes by Place
```
$ curl localhost:5000/earthquakes/by-place?place=California
```

### Filtering Earthquakes by Magnitude
```
$ curl localhost:5000/earthquakes/by-magnitude?min_mag=3.0&max_mag=5.0
```

### Filtering Earthquakes by Date
```
$ curl localhost:5000/earthquakes/by-date?start=2025-03-15&end=2025-04-01
```

### Creating a Hemisphere Analysis Job
```
$ curl -X POST localhost:5000/hemisphere-job -H "Content-Type: application/json" -d '{"min_magnitude": 3.0}'
```

### Checking Job Status
```
$ curl localhost:5000/jobs/<job_id>
```

### Retrieving Job Results
```
$ curl localhost:5000/results/<job_id>
```

## Data Citation

Earthquake data is provided by the United States Geological Survey (USGS) Earthquake Hazards Program. https://earthquake.usgs.gov/