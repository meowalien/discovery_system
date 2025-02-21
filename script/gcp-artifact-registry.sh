
export PROJECT_ID="$(gcloud config get-value project)"

gcloud iam service-accounts create argocd-service-account --description="Service account for argocd" --display-name="argocd SA"

gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:argocd-service-account@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/artifactregistry.reader"

gcloud iam service-accounts keys create ~/argocd-service-account-key.json --iam-account="argocd-service-account@$PROJECT_ID.iam.gserviceaccount.com"

kubectl create -n argocd secret docker-registry gcp-artifact-registry --docker-server=asia-east1-docker.pkg.dev --docker-email="argocd-service-account@$PROJECT_ID.iam.gserviceaccount.com" --docker-username=_json_key --docker-password="$(cat ~/argocd-service-account-key.json)"

#gcloud auth configure-docker asia-east1-docker.pkg.dev

docker pull gcr.io/heptio-images/ks-guestbook-demo:0.2

docker tag gcr.io/heptio-images/ks-guestbook-demo:0.2 "asia-east1-docker.pkg.dev/$PROJECT_ID/docker-repo/ks-guestbook-demo:latest"

docker push "asia-east1-docker.pkg.dev/$PROJECT_ID/docker-repo/ks-guestbook-demo:latest"