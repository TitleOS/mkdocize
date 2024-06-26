# mkdocize

### Description
An agnostic DockerImage for cloning, building, and rendering a mkdocs wiki hosted in a git repo. The container will rebuild whenever changes are commited to the repo.


### Usage
Build the DockerFile and modify the following example docker-compose.yml with ports as you wish.

```yaml
version: '3'

services:
  wiki:
    build: .
    ports:
      - "8000:8000"  # MkDocs HTTP server
      - "9000:9000"  # Webhook listener 
```
Once the container is running, create a Webhook on your repo that posts to the Webhook listener port whenever a push is commited.