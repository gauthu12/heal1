
import jenkins
import json
from datetime import datetime

JENKINS_URL = 'http://localhost:8080'
USERNAME = 'admin'
API_TOKEN = 'aerrt334434'
VIEW_NAME = 'DevOps-Jobs'

server = jenkins.Jenkins(JENKINS_URL, username=USERNAME, password=API_TOKEN)

# Track retries
retry_tracker = {}

def fetch_jobs_status():
    jobs_info = []
    try:
        jobs = server.get_jobs(view_name=VIEW_NAME)
        for job in jobs:
            name = job['name']
            info = server.get_job_info(name)
            color = info['color']
            status = 'Success' if color == 'blue' else 'Running' if color == 'blue_anime' else 'Failed'
            retries_left = 3 - retry_tracker.get(name, 0)
            jobs_info.append({'name': name, 'status': status, 'retries_left': retries_left})
    except Exception as e:
        print(f"Error fetching jobs: {e}")
    return jobs_info

def retry_failed_jobs():
    jobs = fetch_jobs_status()
    for job in jobs:
        if job['status'] == 'Failed' and retry_tracker.get(job['name'], 0) < 3:
            try:
                server.build_job(job['name'])
                retry_tracker[job['name']] = retry_tracker.get(job['name'], 0) + 1
                log_failure(job['name'], f"Auto-retry {retry_tracker[job['name']]} triggered.")
            except Exception as e:
                log_failure(job['name'], f"Retry failed: {e}")

def manual_retry(job_name):
    try:
        server.build_job(job_name)
        retry_tracker[job_name] = retry_tracker.get(job_name, 0) + 1
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
