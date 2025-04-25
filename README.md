# Earthquake Web App

## Help
To view all available routes and their descriptions, visit the `/help` endpoint.
This project utilizes the Earthquake GeoJSON dataset provided by the United States Geological Survey (USGS) to create API endpoints using Flask. The API endpoints are designed to perform Create, Read, and Delete operations on the earthquake dataset, which is stored in a Redis database. These endpoints allow users to interact with seismic event data through flexible queries, including filters by location, magnitude, and date. 

The application features a background jobs system that allows users to submit asynchronous job requests—such as computing statistical summaries based on magnitude bins or analyzing earthquake distribution by hemisphere—and later retrieve the results from the jobs database. The worker component processes these requests, generates visualizations, and stores them for retrieval. The application is containerized using Docker and deployable using Kubernetes, making it portable, scalable, and easy to run across different environments.

Must have [Docker](https://docs.docker.com/get-docker/) and [kubernetes](https://kubernetes.io/releases/download/) installed on your system.

## Earthquake Data Overview
The United States Geological Survey (USGS) Earthquake Hazards Program provides access to real-time and historical earthquake data in GeoJSON format through their public API. The dataset includes detailed information about each seismic event, such as its unique ID, magnitude, geographic coordinates (longitude, latitude, depth), timestamp, location description, and status. Additional attributes include the event type, tsunami occurrence flag, magnitude type, and links to more detailed reports. This data can be filtered by time range, magnitude, and geographic bounds via the API. For this project, we will download the dataset using a specific API query and store the earthquake records in Redis for efficient access, filtering, and analysis.

## File Descriptions
~~~
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
~~~

- [Dockerfile](Dockerfile) - Dockerfile to generate a docker image of our application
- [docker-compose.yml](docker-compose.yml) - Docker-compose file to run the containerized Flask application
- [requirements.txt](requirements.txt) - Required dependencies for the project
- [api.py](./src/api.py) - API endpoints for communication with redis, job management, and data retrieval
- [jobs.py](./src/jobs.py) - Module to handle job requests and queue management
- [worker.py](./src/worker.py) - Worker to process jobs from the queue, generate visualizations, and store results
- [test_api.py](./test/test_api.py) - Integration tests for the Flask application
- [kubernetes/](./kubernetes/) - Configuration files for Kubernetes deployment in test and production environments

## Software Diagram
![image](diagram.svg)

*Software diagram of the Flask Application. Visualization of the containerized application using Docker and how the Flask app interacts with worker and Redis container.*

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

## Hemisphere Analysis

The application includes a hemisphere analysis feature that categorizes earthquakes into four hemispheres based on their coordinates:
- Northeast (latitude ≥ 0, longitude ≥ 0)
- Northwest (latitude ≥ 0, longitude < 0)
- Southeast (latitude < 0, longitude ≥ 0)
- Southwest (latitude < 0, longitude < 0)

### Creating a Hemisphere Analysis Job

To create a hemisphere analysis job, send a POST request to `/hemisphere-job`:

```
POST /hemisphere-job
Content-Type: application/json

{
  "min_magnitude": 3.0  // Optional, defaults to 0 if not provided
}
```

The job will:
1. Filter earthquakes by minimum magnitude (if specified)
2. Count earthquakes in each hemisphere
3. Calculate statistics for each hemisphere (avg magnitude, max magnitude)
4. Generate a bar chart visualization
5. Store the results in the results database

### Retrieving Hemisphere Analysis Results

Once the job is complete, you can retrieve the results using:

```
GET /results/<job_id>
```

The results will include:
- Counts of earthquakes by hemisphere
- Statistics for each hemisphere
- A visualization of the distribution

## Database Architecture

Our application uses Redis to efficiently store and manage data:

1. **Raw Data Database (DB 0)**: Stores the earthquake data with earthquake IDs as keys
2. **Queue Database (DB 1)**: Manages the job queue for asynchronous task processing
3. **Jobs Database (DB 2)**: Stores job information including status and parameters
4. **Results Database (DB 3)**: Stores analysis results and generated visualizations

## Testing

Test scripts are included in the `test` directory to verify the functionality of the API endpoints, job processing, and worker operations. To run tests:

```
$ pytest
```

## Deployment Instructions

### Local Deployment with Docker

#### Build the image

**IMPORTANT**

Before we run the application we must import the dataset. Navigate into the directory where our Dockerfile, and [docker-compose.yml](docker-compose.yml) are located.

Now run:
```
$ docker-compose build
```

#### Run Flask Application Container
Using the [docker-compose.yml](docker-compose.yml) file we can use it to start the Flask application container
```
$ docker-compose up -d
```
**Note:** -d starts the application in the background

Since we mapped to port 5000 in the [docker-compose.yml](docker-compose.yml) to interact with the Flask endpoints we can use `curl localhost:5000/...`

To stop the container use
```
$ docker-compose down
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

## Example Usage

### Loading Data
```
$ curl -X POST localhost:5000/data
```

### Viewing All Earthquakes
```
$ curl localhost:5000/data
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