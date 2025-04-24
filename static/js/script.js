
function retryJob(jobName) {
    fetch('/retry/' + jobName)
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => alert('Error triggering retry!'));
}

// Auto-refresh every 30 seconds
setTimeout(() => {
    window.location.reload();
}, 30000);
