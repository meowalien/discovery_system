export PROJECT_ID="$(gcloud config get-value project)"

gcloud iam service-accounts create github-actions \
    --description="GitHub Actions for pushing to Artifact Registry" \
    --display-name="GitHub Actions Service Account"

gcloud projects add-iam-policy-binding "$PROJECT_ID"  \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

gcloud iam service-accounts keys create github-actions-key.json \
--iam-account="github-actions@$PROJECT_ID.iam.gserviceaccount.com"