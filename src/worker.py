from jobs import get_job_by_id, update_job_status, q, rd, rdb
import json
import logging
from datetime import datetime
import socket
import os
from matplotlib import pyplot as plt

# Logging setup
loglevel = os.environ.get('LOG_LEVEL', 'INFO').upper()
format_str = f'[%(asctime)s {socket.gethostname()}] %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s: %(message)s'
logging.basicConfig(level=loglevel, format=format_str)

#Results db

def bin_magnitude(mag):
    """Convert a magnitude float into a labeled bin (e.g., '3.0–3.9')"""
    if mag is None:
        return "unknown"
    try:
        lower = int(mag)
        upper = lower + 0.9
        return f"{lower}.0-{upper:.1f}"
    except:
        return "invalid"


def create_chart(freq_dict):
    """
    Generate and save a bar chart of earthquake magnitude bins.
    """
    labels = sorted(freq_dict.keys())
    counts = [freq_dict[label] for label in labels]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color='skyblue', edgecolor='black')
    plt.xlabel('Magnitude Bin')
    plt.ylabel('Number of Earthquakes')
    plt.title('Earthquake Magnitude Distribution')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('magnitude_distribution.png')
    plt.close()

def determine_hemisphere(lat, lon):
    """
    Determine which hemisphere a coordinate falls into
    """
    if lat >= 0 and lon >= 0:
        return "Northeast"
    elif lat >= 0 and lon < 0:
        return "Northwest"
    elif lat < 0 and lon >= 0:
        return "Southeast"
    else:  # lat < 0 and lon < 0
        return "Southwest"

def do_hemisphere_work(jobid, job):
    """
    Process a hemisphere analysis job
    """
    # Extract job parameters
    min_magnitude = job.get('min_magnitude', 0)
    
    # Dictionary to track earthquake counts by hemisphere
    hemisphere_counts = {
        "Northeast": 0,
        "Northwest": 0,
        "Southeast": 0,
        "Southwest": 0
    }
    
    # Dictionary to track magnitude statistics by hemisphere
    hemisphere_stats = {
        "Northeast": {"sum": 0, "max": 0, "count": 0},
        "Northwest": {"sum": 0, "max": 0, "count": 0},
        "Southeast": {"sum": 0, "max": 0, "count": 0},
        "Southwest": {"sum": 0, "max": 0, "count": 0}
    }
    
    # Process all earthquakes in Redis
    total_processed = 0
    for key in rd.keys():
        try:
            quake = json.loads(rd.get(key))
            properties = quake.get('properties', {})
            geometry = quake.get('geometry', {})
            
            # Apply magnitude filter
            mag = properties.get('mag')
            if mag is None or mag < min_magnitude:
                continue
                
            # Get earthquake coordinates
            coordinates = geometry.get('coordinates')
            if not coordinates or len(coordinates) < 2:
                continue
                
            lon = coordinates[0]
            lat = coordinates[1]
            
            # Determine hemisphere
            hemisphere = determine_hemisphere(lat, lon)
            
            # Update counts
            hemisphere_counts[hemisphere] += 1
            
            # Update statistics
            hemisphere_stats[hemisphere]["sum"] += mag
            hemisphere_stats[hemisphere]["count"] += 1
            if mag > hemisphere_stats[hemisphere]["max"]:
                hemisphere_stats[hemisphere]["max"] = mag
            
            total_processed += 1
            
        except Exception as e:
            logging.warning(f"Failed to process record {key}: {e}")
    
    # Calculate average magnitudes
    for hemisphere in hemisphere_stats:
        if hemisphere_stats[hemisphere]["count"] > 0:
            hemisphere_stats[hemisphere]["avg"] = hemisphere_stats[hemisphere]["sum"] / hemisphere_stats[hemisphere]["count"]
        else:
            hemisphere_stats[hemisphere]["avg"] = 0
        
        # Clean up the dictionary
        del hemisphere_stats[hemisphere]["sum"]
    
    # Prepare result
    result = {
        "counts_by_hemisphere": hemisphere_counts,
        "stats_by_hemisphere": hemisphere_stats,
        "total_processed": total_processed
    }
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    
    hemispheres = list(hemisphere_counts.keys())
    counts = list(hemisphere_counts.values())
    
    plt.bar(hemispheres, counts, color=['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3'])
    
    plt.xlabel('Hemisphere')
    plt.ylabel('Number of Earthquakes')
    plt.title('Earthquake Distribution by Hemisphere')
    plt.tight_layout()
    plt.savefig('/hemisphere_distribution.png')
    plt.close()
    
    # Store results in Redis
    rdb.hset(jobid, 'result', json.dumps(result))
        
    # Save and store the chart
    with open('/hemisphere_distribution.png', 'rb') as f:
        img = f.read()
    rdb.hset(jobid, 'image', img)
    
    update_job_status(jobid, 'complete')
    logging.info(f"[Worker] Hemisphere job {jobid} completed. Analyzed {total_processed} earthquakes.")

@q.worker
def do_work(jobid):
    """
    Worker to compute frequency of earthquakes in magnitude bins for a given job.
    Assumes job contains filtering logic if needed (e.g., region/type).

    """
    logging.info(f"[Worker] Starting job: {jobid}")
    update_job_status(jobid, 'in progress')

    job = get_job_by_id(jobid)

    job_type = job.get('job_type', 'magnitude')

    if job_type == 'hemisphere':
        do_hemisphere_work(jobid, job)
    else:    
        result = {}
        for key in rd.keys():
            try:
                quake = json.loads(rd.get(key))
                mag = quake.get("properties", {}).get("mag")
                bin_label = bin_magnitude(mag)
                result[bin_label] = result.get(bin_label, 0) + 1
            except Exception as e:
                logging.warning(f"Failed to process record {key}: {e}")

        rdb.hset(jobid,'result', json.dumps(result))

        create_chart(result)
        with open('magnitude_distribution.png','rb') as f:
            img = f.read()
        rdb.hset(jobid,'image', img)


        update_job_status(jobid, 'complete')
        logging.info(f"[Worker] Job {jobid} completed. Binned {sum(result.values())} earthquakes.")


if __name__ == "__main__":
    # Start the worker
    logging.info("Starting worker...")
    do_work()
