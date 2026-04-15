# OpenDataZurich data in Renkulab

This repository is an example of how to work with OpenDataZurich data in Renkulab. The Dockerfile defines a session launcher with all the necessary packages installed.

[Play.ipynb](Play.ipynb) is a Jupyter notebook that demonstrates how to load and plot OpenDataZurich data. The `src` folder contains a helper package and a script that can be used for exploring the data as well.

## Usage

Try it out in Renkulab!

https://renkulab.io/v2/projects/cramakri/opendata-zh

## Local development

Run container for debugging
```bash
docker run -it --rm \
  -p 8888:8888 \
  -v $(pwd):/home/jovyan/work \
  -e NB_UID=1000 \
  -e NB_GID=1000 \
  ghcr.io/opendatazurich/opendatazurich_renku:sha-e21081d \
  /bin/bash
```


Run and start Jupyter server with (with environment variables for tabular dataset)

```bash
docker run -it --rm \
  -p 8888:8888 \
  -v $(pwd):/home/jovyan/work \
  -e NB_UID=1000 \
  -e NB_GID=1000 \
  -e PACKAGE_ID="politik_abstimmungen_seit1933" \
  -e RESOURCE_ID="3e87b102-f19c-47f4-ab50-a679b51cf77e" \
  ghcr.io/opendatazurich/opendatazurich_renku:sha-e21081d \
  /bin/bash -c "cd /home/jovyan/work && bash post-init.sh && \
  jupyter server --ServerApp.ip=0.0.0.0 --ServerApp.port=8888 --ServerApp.base_url=$RENKU_BASE_URL_PATH --ServerApp.token='' --ServerApp.password='' --ServerApp.allow_remote_access=true --ContentsManager.allow_hidden=true --ServerApp.allow_origin='*'"
```


Run and start Jupyter server with (with environment variables for geo dataset)
```bash
docker run -it --rm \
  -p 8888:8888 \
  -v $(pwd):/home/jovyan/work \
  -e NB_UID=1000 \
  -e NB_GID=1000 \
  -e PACKAGE_ID="geo_oeffentlich_zugaengliche_parkplaetze_dav" \
  -e RESOURCE_ID="2ed0038f-974c-4cb8-b7fd-3cf5217e9d6d" \
  ghcr.io/opendatazurich/opendatazurich_renku:sha-e21081d \
  /bin/bash -c "cd /home/jovyan/work && bash post-init.sh && \
  jupyter server --ServerApp.ip=0.0.0.0 --ServerApp.port=8888 --ServerApp.base_url=$RENKU_BASE_URL_PATH --ServerApp.token='' --ServerApp.password='' --ServerApp.allow_remote_access=true --ContentsManager.allow_hidden=true --ServerApp.allow_origin='*'"
```
