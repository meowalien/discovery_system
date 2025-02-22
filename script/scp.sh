#!/bin/bash

# 檢查是否有帶 IP 參數
if [ -z "$1" ]; then
  echo "Usage: $0 <IP_ADDRESS> <SRC_PATH> <DEST_PATH>"
  exit 1
fi

remote_ip=$1
src_path=$2
dest_path=$3


scp -i "$PWD/google_compute_engine" \
    "${src_path}" \
    jackyli@"${remote_ip}":"${dest_path}"

#ssh -i /Users/jackyli/.ssh/google_compute_engine \
#    jackyli@"${remote_ip}" \
#    "minikube kubectl -- apply -n argocd -f ~/application.yaml"