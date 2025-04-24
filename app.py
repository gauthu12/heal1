from flask import Flask, render_template, jsonify, request
from jenkins_helper import fetch_jobs_status, fetch_node_status, manual_retry, fetch_analytics_data
from scheduler import start_job_monitor, start_node_monitor

app = Flask(__name__)

# Start background monitors
start_job_monitor()
start_node_monitor()

@app.route('/')
def dashboard():
    jobs = fetch_jobs_status()
    nodes = fetch_node_status()
    return render_template('index.html', jobs=jobs, nodes=nodes)

@app.route('/retry/<job_name>')
def retry_job(job_name):
    message = manual_retry(job_name)
    return jsonify({'message': message})

@app.route('/analytics')
def analytics():
    return jsonify(fetch_analytics_data())

# Chatbot endpoint
@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message','').lower()
    if 'failed' in msg:
        failed = [j['name'] for j in fetch_jobs_status() if j['status']=='Failed']
        return jsonify({'reply': f"Failed jobs: {', '.join(failed)}. Retry one?"})
    if 'nodes down' in msg:
        down = sum(1 for n in fetch_node_status() if n['status']=='Offline')
        return jsonify({'reply': f"{down} nodes are offline."})
    return jsonify({'reply': "Sorry, I didn't get that. Try 'list failed jobs' or 'nodes down'."})

if __name__ == '__main__':
    app.run(debug=True)
