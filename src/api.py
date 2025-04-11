from flask import Flask, request, jsonify
import requests
import redis
import json
from jobs import add_job, get_job_by_id, rd, jdb


app = Flask(__name__)


def get_data():
    """
        Load earthquake dataset
    """
    response = requests.get(url='https://earthquake.usgs.gov/fdsnws/event/1/query.geojson?starttime=2025-03-12%2000:00:00&endtime=2025-04-11%2023:59:59&minmagnitude=2.5&orderby=time')
    return json.loads(response.content)['features']




@app.route('/jobs', methods=['GET'])
def get_jobs():
    """
        Gets all jobs in the redis database
    """
    return jsonify(jdb.keys())
@app.route('/jobs/<jobid>', methods=['GET'])
def get_job(jobid):
    """
        Gets a specific job by unique uuid
    """
    return get_job_by_id(jobid)


@app.route('/result/<jobid>', methods=['GET'])

def get_result(jobid):
"""
return specific result of a job
"""

    try:
        if get_job_by_id(jobid)['status'] != 'complete':
            return jsonify({'message':'job is not finished yet'})
        return json.loads(rdb.get(jobid))
    except:
        logging.error(f'job_id not found: {jobid}')
        return jsonify({'message': 'job_id not found'})



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
                rd.set(gene['id'], json.dumps(earthquake))
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

    earthquake_place = request.args.get('place')
    results = []

    for keys in rd.keys():
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
            if (min_magnitude is None or magnitude >= min_magnitude) and (max_magnitudeis None or magnitude <= max_magnitude):
                return results.append(record)

    return jsonify(results)


@app.route('/earthquake', methods=['GET'])

def get_earthquake_by_date():
    """
    Filter the earthquake by date
    """
    start_date = requests.args.get('start')
    end_date = requests.args.get('end')

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
            resilts.append(record)

    return jsonify(results)
    



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")




