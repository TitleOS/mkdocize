# mkdocize

### Description
An agnostic DockerImage for cloning, building, and rendering a mkdocs wiki hosted in a git repo. The container will rebuild whenever changes are commited to the repo.


### Usage
Build the DockerFile and modify the following example docker-compose.yml with ports as you wish. REPO_URL should be set to the http clone url for your git mkdocs repo, such as a wiki. REPO_PATH is the local path in the container that the repo will be stored, be sure to include /wiki/ as the root.

```yaml
version: '3'
environment:
  - REPO_URL=http://gitea.example.com/different-user/different-repo.git
  - REPO_PATH=/wiki/docs
services:
  wiki:
    build: .
    ports:
      - "8000:8000"  # MkDocs HTTP server
      - "9000:9000"  # Webhook listener 
```
Once the container is running, create a Webhook on your repo that posts to /webhook on the Webhook listener port whenever a push is commited.