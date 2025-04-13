# Earthquake Web App
This project utilizes the Earthquake GeoJSON dataset provided by the United States Geological Survey (USGS) to create API endpoints using Flask. The API endpoints are designed to perform Create, Read, and Delete operations on the earthquake dataset, which is stored in a Redis database. These endpoints allow users to interact with seismic event data through flexible queries, including filters by location, magnitude, and date. 

Additionally, this project features a background jobs system that allows users to submit asynchronous job requests—such as computing statistical summaries or extracting top-impact events—and later retrieve the results from the jobs database. The application is containerized using Docker and optionally deployable using Kubernetes, making it portable, scalable, and easy to run across different environments.

Must have [Docker](https://docs.docker.com/get-docker/) and [kubernetes](https://kubernetes.io/releases/download/) installed on your system.

## Earthquake Data Overview
The [City of Austin open data portal](https://data.austintexas.gov/Transportation-and-Mobility/Austin-MetroBike-Trips/tyfh-5r8s/about_data) provides access to the Austin MetroBike Trips dataset available in both CSV and JSON formats, but is limited to 1000 rows of data through their endpoint. Instead we will download the data as a whole using their download feature. Overall, the dataset contains information about bike trips, their associated trip IDs, membership type, bicycle IDs, bicycle types, checkout times, trip duration, and kiosk location, among others.

## File Descriptions
The United States Geological Survey (USGS) Earthquake Hazards Program provides access to real-time and historical earthquake data in GeoJSON format through their public API. The dataset includes detailed information about each seismic event, such as its unique ID, magnitude, geographic coordinates (longitude, latitude, depth), timestamp, location description, and status. Additional attributes include the event type, tsunami occurrence flag, magnitude type, and links to more detailed reports. This data can be filtered by time range, magnitude, and geographic bounds via the API. For this project, we will download the dataset using a specific API query and store the earthquake records in Redis for efficient access, filtering, and analysis.
~~~
Austin-MetroBike-Share-Web-App/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    ├── software_diagram.svg
    ├── README.md
    ├── kubernetes
    ├── prod
    │   ├── app-prod-deployment-flask.yml
    │   ├── app-prod-deployment-redis.yml
    │   ├── app-prod-deployment-worker.yml
    │   ├── app-prod-ingress-flask.yml
    │   ├── app-prod-pvc-redis.yml
    │   ├── app-prod-service-flask.yml
    │   ├── app-prod-service-nodeport-flask.yml
    │   └── app-prod-service-redis.yml
    └── test
    │   ├── app-test-deployment-flask.yml
    │   ├── app-test-deployment-redis.yml
    │   ├── app-test-deployment-worker.yml
    │   ├── app-test-ingress-flask.yml
    │   ├── app-test-pvc-redis.yml
    │   ├── app-test-service-flask.yml
    │   ├── app-test-service-nodeport-flask.yml
    │   └── app-test-service-redis.yml
    ├── data
    │   └── .gitcanary
    ├── test
    │   └── bike_share_api.py
    └── src
      ├── bike_share_api.py
      ├── jobs.py
      └── worker.py
~~~

- [Dockerfile](Dockerfile) Dockerfile to generate a docker image of our application
- [docker-compose.yml](docker-compose.yml) docker-compose file to run the containerized Flask application
- [requirements.txt](requirements.txt) Required dependencies for the project
- [bike_share_api.py](./src/bike_share_api.py) API endpoints for communicaton to redis, jobs, and GET requests
- [jobs.py](./src/jobs.py) Module to handle jobs requests 
- [worker.py](./src/worker.py) worker to handle jobs in the redis database (queue) as they come in and then post results (plots) in the results database
- [test_gene_api.py](./test/test_gene_api.py) Integration tests for flask app

## Software Diagram
![image](diagram.svg)

*Software diagram of the Flask Application. Visualization of the containerized application using Docker and how the Flask app interacts with worker and Redis container.*

## Running the application using Docker
### Build the image

**IMPORTANT**

Before we run the application we must import the dataset. Navigate into the directory where our Dockerfile, and [docker-compose.yml](docker-compose.yml) are located and run this command to download the dataset.
~~~
$ wget https://data.austintexas.gov/api/views/tyfh-5r8s/rows.csv?accessType=DOWNLOAD -O Austin_MetroBike_Trips.csv
~~~

Now run 
~~~
$ docker-compose build
~~~

### Run Flask Application Container
Using the [docker-compose.yml](docker-compose.yml) file we can use it to start the Flask application container
~~~
$ docker-compose up -d
~~~
**Note:** -d starts the application in the background

Since we mapped to port 5000 in the [docker-compose.yml](docker-compose.yml) to interact with the Flask endpoints we can use `curl localhost:5000/...`

To stop the container use
~~~
$ docker-compose down
~~~
