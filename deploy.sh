#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="maps-agent"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
SERVICE_ACCOUNT="maps-agent-sa@$PROJECT_ID.iam.gserviceaccount.com"

echo "Deploying $SERVICE_NAME to Google Cloud Run in $REGION..."

# 1. Build the unified Docker image using Cloud Build
echo "Building Docker image: $IMAGE_NAME..."
gcloud builds submit --tag $IMAGE_NAME

# 2. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --service-account $SERVICE_ACCOUNT \
  --memory 1Gi \
  --set-env-vars="PROJECT_ID=$PROJECT_ID,MODEL_NAME=gemini-2.0-flash" \
  --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest,VITE_GOOGLE_MAPS_API_KEY=VITE_GOOGLE_MAPS_API_KEY:latest"

echo "Deployment complete! ✅"
