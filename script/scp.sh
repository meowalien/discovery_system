#!/bin/bash

# 檢查是否有帶 IP 參數
if [ -z "$1" ]; then
  echo "Usage: $0 <IP_ADDRESS>"
  exit 1
fi

remote_ip=$1

# -i 後面是你的金鑰路徑，請自行調整
# 這裡使用 $PWD/application.yaml 表示「執行當下的資料夾」底下的 application.yaml
scp -i /Users/jackyli/.ssh/google_compute_engine \
    "$PWD/infrastructure/application.yaml" \
    jackyli@"${remote_ip}":~/application.yaml

ssh -i /Users/jackyli/.ssh/google_compute_engine \
    jackyli@"${remote_ip}" \
    "minikube kubectl -- apply -n argocd -f ~/application.yaml"