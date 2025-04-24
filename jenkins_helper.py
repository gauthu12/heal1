import jenkins, json
from datetime import datetime
from collections import Counter

JENKINS_URL = 'http://localhost:8080'
USERNAME    = 'admin'
API_TOKEN   = 'aerrt334434'
VIEW_NAMES  = ['test','prod','devops']
TEAMS_WEBHOOK = 'https://your.webhook.here'  # replace

server = jenkins.Jenkins(JENKINS_URL, username=USERNAME, password=API_TOKEN)
retry_tracker = {}
failure_logs = 'failure_logs.json'

def log_failure(job, reason):
    try:
        data = json.load(open(failure_logs))
    except:
        data = {}
    data.setdefault(job,[]).append({'time':datetime.now().isoformat(),'reason':reason})
    json.dump(data, open(failure_logs,'w'), indent=2)

def traverse(folder):
    out=[]
    try:
        jobs = server.get_jobs(folder)
    except:
        return []
    for j in jobs:
        full = j['fullname']
        cls  = j['_class']
        if 'Folder' in cls:
            out+=traverse(full)
        else:
            info = server.get_job_info(full)
            color=info.get('color','')
            status = 'Success' if color=='blue' else 'Running' if 'anime' in color else 'Failed'
            done = int(retry_tracker.get(full,0))
            left = max(0,3-done)
            out.append({'name':full,'status':status,'retries_left':left})
    return out

def fetch_jobs_status():
    alljobs=[]
    for v in VIEW_NAMES:
        for j in server.get_jobs(view_name=v):
            if 'Folder' in j['_class']:
                alljobs+=traverse(j['fullname'])
            else:
                alljobs+=traverse(j['fullname'])
    return alljobs

def retry_failed_jobs():
    for job in fetch_jobs_status():
        if job['status']=='Failed' and int(retry_tracker.get(job['name'],0))<3:
            try:
                server.build_job(job['name'])
                retry_tracker[job['name']]=int(retry_tracker.get(job['name'],0))+1
                log_failure(job['name'],f"Auto-retry #{retry_tracker[job['name']]}")
            except Exception as e:
                log_failure(job['name'],f"Retry error: {e}")

def manual_retry(job):
    try:
        server.build_job(job)
        retry_tracker[job]=int(retry_tracker.get(job,0))+1
        log_failure(job,"Manual retry")
        return f"Retried {job}"
    except Exception as e:
        log_failure(job,f"Manual retry error: {e}")
        return str(e)

def fetch_node_status():
    nodes = server.get_nodes()
    out=[]
    for n in nodes:
        info=server.get_node_info(n['name'])
        stat = 'Online' if info['offline']==False else 'Offline'
        out.append({'name':n['name'],'status':stat})
    return out

def fetch_analytics_data():
    jobs = fetch_jobs_status()
    nodes=fetch_node_status()
    sc=Counter(j['status'] for j in jobs)
    return {
      'status_counts':sc,
      'retry_trends':{j:len(json.load(open(failure_logs)).get(j,[])) for j in sc},
      'node_counts':Counter(n['status'] for n in nodes)
    }

# Teams notification (fires after each retry cycle)
def notify_teams(job):
    import requests
    msg = {'text':f"Job *{job}* failed 3 times."}
    requests.post(TEAMS_WEBHOOK, json=msg)
