#!/bin/bash

cd "$(dirname "$0")"
mkdir -p build
rsync -va Dockerfile ../main.py ../creds.yaml ../dist build

docker build -t juncture-webapp build
rm -rf build

docker run -it -p 8080:8080 juncture-webapp
