
from flask import Flask, render_template, jsonify
from jenkins_helper import fetch_jobs_status, manual_retry
from scheduler import start_job_monitor
import json
from collections import Counter

app = Flask(__name__)

# Start background monitoring when app starts
start_job_monitor()

@app.route('/')
def dashboard():
    jobs = fetch_jobs_status()
    return render_template('index.html', jobs=jobs)

@app.route('/retry/<job_name>')
def retry_job(job_name):
    message = manual_retry(job_name)
    return jsonify({'message': message})

@app.route('/analytics')
def analytics_data():
    jobs = fetch_jobs_status()
    status_counts = Counter(job['status'] for job in jobs)
    
    with open('failure_logs.json', 'r') as f:
        logs = json.load(f)
    
    retry_trends = {job: len(entries) for job, entries in logs.items()}
    
    return jsonify({
        'status_counts': status_counts,
        'retry_trends': retry_trends,
        'failure_frequency': retry_trends
    })

if __name__ == '__main__':
    app.run(debug=True)
