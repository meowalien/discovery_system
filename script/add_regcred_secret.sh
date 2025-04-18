

export PROJECT_ID="$(gcloud config get-value project)"
kubectl create secret docker-registry gcp-artifact-registry \
  --docker-server=asia-east1-docker.pkg.dev \
  --docker-username=_json_key \
  --docker-password="$(cat ./argocd-service-account-key.json)" \
  --docker-email="argocd-service-account@$PROJECT_ID.iam.gserviceaccount.com"