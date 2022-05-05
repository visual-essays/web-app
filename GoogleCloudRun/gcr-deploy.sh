#!/bin/bash

GCP_PROJECT='visual-essays'

GCR_SERVICE=${1:-mdrender}

gcloud config set project ${GCP_PROJECT}
gcloud config set compute/region us-central1
gcloud config set run/region us-central1

rsync -va ../main.py .
rsync -va ../static .
gcloud builds submit --tag gcr.io/${GCP_PROJECT}/${GCR_SERVICE}
rm -rf main.py static
gcloud beta run deploy ${GCR_SERVICE} --image gcr.io/${GCP_PROJECT}/${GCR_SERVICE} --allow-unauthenticated --platform managed --memory 1Gi
