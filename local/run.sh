#!/bin/bash

cd "$(dirname "$0")"
mkdir -p build
rsync -va Dockerfile build
rsync -va ../main.py build

docker build -t juncture-webapp build
docker run -it -p 8080:8080 juncture-webapp

rm -rf build