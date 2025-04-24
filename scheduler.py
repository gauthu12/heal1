
from apscheduler.schedulers.background import BackgroundScheduler
from jenkins_helper import retry_failed_jobs

def start_job_monitor():
    scheduler = BackgroundScheduler()
    scheduler.add_job(retry_failed_jobs, 'interval', seconds=30)
    scheduler.start()
