from flask import Flask, request, jsonify
import requests
import redis
import json
from jobs import add_job, get_job_by_id, add_hemisphere_job, rd, jdb
import datetime
import logging
import os


app = Flask(__name__)
#Start logger
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

#Get redis host from env vars
redis_ip = os.environ.get("REDIS_IP", "redis-db")
redis_port = 6379

#Setup redis
rd = redis.Redis(host = redis_ip, port=redis_port, db=0)
jobs_db = redis.Redis(host=redis_ip, port=redis_port, db=2)
rdb = redis.Redis(host=redis_ip, port=redis_port, db=3)


def get_data():
    """
        Load earthquake dataset
    """
    response = requests.get(url='https://earthquake.usgs.gov/fdsnws/event/1/query.geojson?starttime=2025-03-12%2000:00:00&endtime=2025-04-11%2023:59:59&minmagnitude=2.5&orderby=time')
    return json.loads(response.content)['features']

@app.route('/jobs', methods=['POST'])
def create_job():
    """
    Route to send a job to redis database

    Methods:

    Post: send a job to redis database 

    """


    try:
        job_info = request.get_json()

        if not job_info:
            return jsonify({"error": "No job info given"})

        if 'start' not in job_info or 'end' not in job_info:
            return jsonify({"error": "Missing start or end"})
        
        job = add_job(job_info['start'], job_info['end'])

        return jsonify({"id" : job['id'], "status" : job['status']})
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        return jsonify({"error" : str(e)})
    
@app.route('/jobs', methods = ['GET'])
def list_job_ids():
    """
    Get all jobs in the redis databse
    """

    try:
        jobs = []
        for key in list(jobs_db.keys()):
            jobid = key.decode('utf-8')
            jobs.append(jobid)
        
        return jsonify(jobs)
    
    except Exception as e:
        logger.error(f"Error listing job ids: {e}")
        return jsonify({"error": str(e)})
    
@app.route('/jobs/<job_id>', methods=['GET'])
def get_jobinfo(job_id):
    """
    get a specfic jobs by ID

    """

    try:
        job = get_job_by_id(job_id)


        if not job:
            return jsonify({"error" : f"Job {job_id} not found"})

        return jsonify(job)
    
    except Exception as e:
        logger.error(f"Error getting job {job_id} info: {e}")
        return jsonify({"error" : str(e)})

@app.route('/results/<job_id>', methods=['GET'])
def get_job_results(job_id):
    try:
        job = get_job_by_id(job_id)
        if not job:
            return jsonify({"Error": f"Job {job_id} not found"})
        
        status = job.get('status')

        if status != 'complete':
            return jsonify({"message" : f"Job {job_id} has not been completed yet", 
                           "status" : status})

        results = rdb.get(job_id)
        if not results:
            return jsonify({"message" : f"No results found for job {job_id}",
                            "status": status})
        
        return jsonify(json.loads(results))
    
    except Exception as e:
        logger.error(f"Error getting results for job {job_id}: {e}")
        return jsonify({"error": str(e)})





@app.route('/data', methods=['POST', 'GET', 'DELETE'])
def handle_data():
    """
        Route perfrom POST, GET, DELETE requests on earthquake dataset

        Methods:
            POST: Load entire dataset into redis database
            GET: Return entire gene dataset from redis database in JSON
            DELETE: Delete everything redis
    """
    if request.method == 'POST':
        try:
            data = get_data()
            for earthquake in data:
                rd.set(earthquake['id'], json.dumps(earthquake))
            return jsonify({'message': 'Data added successfully'})
        except:
            return jsonify({'message': 'Data was NOT added successfully'})
    if request.method == 'GET':
        result = []
        for key in rd.keys():
            result.append(json.loads(rd.get(key)))
        return jsonify(result)
    if request.method == 'DELETE':
        rd.flushdb()
        return jsonify({'message': 'Data deleted successfully'})



@app.route('/earthquake', methods=['GET'])
def get_genes():
    """
        Return a list of unique earthquake
    """
    return jsonify(rd.keys())

@app.route('/earthquake/<earthquake_id>', methods=['GET'])
def get_specific_gene(earthquake_id):
    """
        Return gene information of a specific HGNC_ID
    """
    if rd.exists(earthquake_id):
        return json.loads(rd.get(earthquake_id))

    return jsonify({'message': 'earthquake_id not found'})


@app.route('earthquakes', methods=['GET'])

def get_earthquake_by_place():
    """
        Filter the earthquake dataset by place
    """

    place_query = request.args.get('place')
    results = []

    for key in rd.keys():
        record = json.loads(rd.get(key))
        place = record.get('properties').get('place')
        if place_query and place_query.lower() in place.lower():
            results.append(record)


    return jsonify(results)


@app.route('/earthquake', methods=['GET'])
def get_earthquake_by_magnitude():

    """
    Filter the earthquake by magnitude in a range
    """
    min_magnitude = request.args.get('min_mag',type=float)
    max_magnitude = request.args.get('max_mag',type=float)

    results =[]

    for key in rd.keys():
        record = json.loads(rd.get(key))
        magnitude = record.get('properties').get('mag')
        if isinstance (magnitude, (int, float )): # check the magnitude type 
            if (min_magnitude is None or magnitude >= min_magnitude) and (max_magnitude is None or magnitude <= max_magnitude):
                return results.append(record)

    return jsonify(results)


@app.route('/earthquake', methods=['GET'])
def get_earthquake_by_date():
    """
    Filter the earthquake by date
    """
    start_date_str = str(requests.args.get('start'))
    end_date_str = str(requests.args.get('end'))

    try:
        start_ts = int(datetime.strptime(start_date_str, '%Y-%m-%d').timestamp() * 1000)
        end_ts = int(datetime.strptime(end_date_str, '%Y-%m-%d').timestamp() * 1000)

    except:
        return jsonify({'error': 'Invalid date format'})

    results = []

    for key in rd.keys():
        record = json.loads(rd.get(key))
        time = record.get('properties').get('time')

        if start_ts <= time <= end_ts:
            results.append(record)

    return jsonify(results)

@app.route('/hemisphere-job', methods=['POST'])
def create_hemisphere_job():
    """
    Route to create a job that analyzes earthquakes by hemisphere
    
    Methods:
    POST: Send a hemisphere analysis job to redis database
    """
    try:
        job_info = request.get_json()

        # Optional parameter
        min_magnitude = job_info.get('min_magnitude', 0) if job_info else 0
        
        # Create the job
        job = add_hemisphere_job(min_magnitude=min_magnitude)

        return jsonify({"id": job['id'], "status": job['status']})
    
    except Exception as e:
        logger.error(f"Error creating hemisphere job: {e}")
        return jsonify({"error": str(e)})
    



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")




