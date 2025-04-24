from apscheduler.schedulers.background import BackgroundScheduler
from jenkins_helper import retry_failed_jobs

def start_job_monitor():
    sched = BackgroundScheduler()
    sched.add_job(retry_failed_jobs,'interval',seconds=30)
    sched.start()

def start_node_monitor():
    # Node checks could go here if you want separate logic
    pass
