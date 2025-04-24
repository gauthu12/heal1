
import jenkins
import json
from datetime import datetime

JENKINS_URL = 'http://localhost:8080'
USERNAME = 'admin'
API_TOKEN = 'aerrt334434'
VIEW_NAME = 'test1'  # Assuming 'test1' is the view name

server = jenkins.Jenkins(JENKINS_URL, username=USERNAME, password=API_TOKEN)

retry_tracker = {}

def traverse_folders(base_path):
    jobs_info = []
    try:
        jobs = server.get_jobs(base_path)
        for job in jobs:
            job_full_name = job['fullname']
            job_class = job['_class']

            if 'Folder' in job_class:
                jobs_info.extend(traverse_folders(job_full_name))
            else:
                info = server.get_job_info(job_full_name)
                color = info.get('color', '')
                status = ('Success' if color == 'blue' else 
                          'Running' if 'anime' in color else 'Failed')
                retries_done = int(retry_tracker.get(job_full_name, 0) or 0)
                retries_left = max(0, 3 - retries_done)
                jobs_info.append({'name': job_full_name, 'status': status, 'retries_left': retries_left})
    except Exception as e:
        print(f"Error traversing path '{base_path}': {e}")
    return jobs_info

def fetch_jobs_status():
    return traverse_folders(VIEW_NAME)

def retry_failed_jobs():
    jobs = fetch_jobs_status()
    for job in jobs:
        retries_done = int(retry_tracker.get(job['name'], 0) or 0)
        if job['status'] == 'Failed' and retries_done < 3:
            try:
                server.build_job(job['name'])
                retry_tracker[job['name']] = retries_done + 1
                log_failure(job['name'], f"Auto-retry attempt {retry_tracker[job['name']]}: Triggered due to job failure.")
            except Exception as e:
                log_failure(job['name'], f"Auto-retry failed: {e}")

def manual_retry(job_name):
    retries_done = int(retry_tracker.get(job_name, 0) or 0)
    try:
        server.build_job(job_name)
        retry_tracker[job_name] = retries_done + 1
        log_failure(job_name, f"Manual retry triggered.")
        return f"Manual retry for {job_name} triggered."
    except Exception as e:
        log_failure(job_name, f"Manual retry failed: {e}")
        return f"Failed to retry {job_name}: {e}"

def log_failure(job_name, reason):
    try:
        with open('failure_logs.json', 'r') as f:
            logs = json.load(f)
    except:
        logs = {}
    logs.setdefault(job_name, []).append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reason': reason
    })
    with open('failure_logs.json', 'w') as f:
        json.dump(logs, f, indent=4)
