#!/bin/bash

GCP_PROJECT='visual-essays'

GCR_SERVICE=${1:-custom}

gcloud config set project ${GCP_PROJECT}
gcloud config set compute/region us-central1
gcloud config set run/region us-central1

gcloud builds submit --tag gcr.io/${GCP_PROJECT}/${GCR_SERVICE}
gcloud beta run deploy ${GCR_SERVICE} --image gcr.io/${GCP_PROJECT}/${GCR_SERVICE} --allow-unauthenticated --platform managed --memory 1Gi
