
export PROJECT_ID="$(gcloud config get-value project)"

gcloud iam service-accounts create on-premises-service-account --description="Service account for on-premises machine" --display-name="On-premises SA"

gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:on-premises-service-account@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/artifactregistry.reader"

gcloud iam service-accounts keys create ~/on-premises-service-account-key.json --iam-account="on-premises-service-account@$PROJECT_ID.iam.gserviceaccount.com"

kubectl create secret docker-registry gcp-artifact-registry --docker-server=https://asia-east1-docker.pkg.dev --docker-email="on-premises-service-account@$PROJECT_ID.iam.gserviceaccount.com" --docker-username=_json_key --docker-password="$(cat ~/on-premises-service-account-key.json)"

gcloud auth configure-docker asia-east1-docker.pkg.dev

docker pull busybox

docker tag busybox "asia-east1-docker.pkg.dev/$PROJECT_ID/docker-repo/busybox:latest"

docker push "asia-east1-docker.pkg.dev/$PROJECT_ID/docker-repo/busybox:latest"