# Deploying the Maps Agent to Google Cloud Run

This guide explains how to deploy the unified Maps Agent application to Google Cloud Run. The deployment architecture serves the React frontend statically directly through the FastAPI backend runtime, requiring only a single lightweight Cloud Run container.

## Prerequisites

1. **Google Cloud Project**: You must have a GCP project with billing enabled.
2. **gcloud CLI**: Ensure the Google Cloud SDK is installed and authenticated (`gcloud auth login`).
3. **APIs Enabled**: Ensure the following APIs are enabled in your project:
   - Cloud Run API
   - Cloud Build API
   - Artifact Registry API
   - Vertex AI API (For Gemini)
   - Secret Manager API

## Step 1: Create a Service Account

The agent needs permissions to invoke Vertex AI models (Gemini) and read your profiles from BigQuery.

```bash
# Create the service account
gcloud iam service-accounts create maps-agent-sa \
    --description="Service account for Maps Agent Cloud Run" \
    --display-name="Maps Agent SA"

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:maps-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Grant BigQuery Data Viewer role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:maps-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"
```

## Step 2: Store API Keys in Secret Manager

Do not hardcode API keys! Store them in GCP Secret Manager so Cloud Run can mount them securely.

```bash
# Create GOOGLE_API_KEY secret
echo -n "YOUR_GCP_API_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=-
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
    --member="serviceAccount:maps-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create VITE_GOOGLE_MAPS_API_KEY secret
echo -n "YOUR_MAPS_API_KEY" | gcloud secrets create VITE_GOOGLE_MAPS_API_KEY --data-file=-
gcloud secrets add-iam-policy-binding VITE_GOOGLE_MAPS_API_KEY \
    --member="serviceAccount:maps-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Step 3: Deploy

Once the service account and secrets are configured, execute the deployment script.

```bash
# Review deploy.sh and ensure your PROJECT_ID is correct
./deploy.sh
```

The script will:
1. Trigger Cloud Build to execute the multi-stage `Dockerfile`.
2. Build the React frontend production bundle.
3. Install Python backend dependencies.
4. Push the image to Google Container Registry.
5. Deploy the image to Cloud Run, automatically injecting the secrets as environment variables.

When complete, `gcloud` will output the live HTTPS Service URL for your deployed agent!
