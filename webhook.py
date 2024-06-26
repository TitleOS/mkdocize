import os
import subprocess
from flask import Flask, request
import threading

app = Flask(__name__)
mkdocs_process = None

# Get repo URL and path from environment variables
REPO_URL = os.environ.get('REPO_URL')
REPO_PATH = os.environ.get('REPO_PATH', '/wiki/docs')

if not REPO_URL:
    raise ValueError("REPO_URL environment variable must be set")

def clone_or_pull_repo():
    if not os.path.exists(REPO_PATH):
        subprocess.run(["git", "clone", REPO_URL, REPO_PATH])
    else:
        subprocess.run(["git", "-C", REPO_PATH, "pull"])

def run_mkdocs():
    global mkdocs_process
    mkdocs_process = subprocess.Popen(["mkdocs", "serve", "-f", f"{REPO_PATH}/mkdocs.yml", "-a", "0.0.0.0:8000"])

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Pull the latest changes
        clone_or_pull_repo()
        
        global mkdocs_process
        # Stop the current MkDocs process
        if mkdocs_process:
            mkdocs_process.terminate()
            mkdocs_process.wait()
        
        # Rebuild the site
        subprocess.run(["mkdocs", "build", "-f", f"{REPO_PATH}/mkdocs.yml"])
        
        # Restart MkDocs
        run_mkdocs()
        
        return 'Success', 200
    else:
        return 'Invalid request', 400

if __name__ == '__main__':
    # Initial clone of the repository
    clone_or_pull_repo()
    
    # Start MkDocs initially
    run_mkdocs()
    
    # Start the Flask app to listen for webhooks
    app.run(host='0.0.0.0', port=9000)