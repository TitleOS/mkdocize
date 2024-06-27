import os
import subprocess
from flask import Flask, request
import threading
import logging

app = Flask(__name__)
mkdocs_process = None

# Setup logging for the container
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Get repo URL and path from environment variables
REPO_URL = os.environ.get('REPO_URL')
REPO_PATH = os.environ.get('REPO_PATH', '/wiki/docs')

if not REPO_URL:
    logger.error("REPO_URL environment variable must be set")
    raise ValueError("REPO_URL environment variable must be set")

def clone_or_pull_repo():
    if not os.path.exists(REPO_PATH):
        logger.info(f"Cloning repository from {REPO_URL} to {REPO_PATH}")
        subprocess.run(["git", "clone", REPO_URL, REPO_PATH])
    else:
        logger.info(f"Pulling latest changes in {REPO_PATH}")
        subprocess.run(["git", "-C", REPO_PATH, "pull"])

def run_mkdocs():
    global mkdocs_process
    logger.info("Starting MkDocs server on port 8000")
    mkdocs_process = subprocess.Popen(["mkdocs", "serve", "-f", f"{REPO_PATH}/mkdocs.yml", "-a", "0.0.0.0:8000"])

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        logger.info("Recieved POST to /webhook, updating local repo instance.")
        # Pull the latest changes
        clone_or_pull_repo()
        
        global mkdocs_process
        # Stop the current MkDocs process
        if mkdocs_process:
            mkdocs_process.terminate()
            mkdocs_process.wait()
        
        # Rebuild the site
        subprocess.run(["mkdocs", "build", "-f", f"{REPO_PATH}/mkdocs.yml"])
        logger.info("Rebuilt local mkdocs repo.")
        
        # Restart MkDocs
        run_mkdocs()
        logger.info("Restarted mkdocs rendering server with rebuilt repo.")
        return 'Success', 200
    else:
        logger.warning("Recieved invalid request on /webhook endpoint.")
        return 'Invalid request', 400

if __name__ == '__main__':
    # Initial clone of the repository
    clone_or_pull_repo()
    
    # Start MkDocs initially
    run_mkdocs()
    
    # Start the Flask app to listen for webhooks
    app.run(host='0.0.0.0', port=9000)
    logger.info("Started Webhook listener on port 9000.")