#!/usr/bin/env bash

if [ -z "$1" ]; then
  echo "Usage: $0 <namespace> <service-name> <host-port> <container-port>"
  exit 1
fi

NAMESPACE="$1"
SERVICE_NAME="$2"
HOST_PORT="$3"
CONTAINER_PORT="$4"

# 重新載入 systemd
sudo systemctl daemon-reload

# 啟用、啟動、檢查狀態
sudo systemctl enable port-forward@$NAMESPACE:$SERVICE_NAME:$HOST_PORT:$CONTAINER_PORT.service
sudo systemctl start port-forward@$NAMESPACE:$SERVICE_NAME:$HOST_PORT:$CONTAINER_PORT.service
sudo systemctl status port-forward@$NAMESPACE:$SERVICE_NAME:$HOST_PORT:$CONTAINER_PORT.service


# sudo systemctl status port-forward@argocd:argocd-server:8080:80.service
# sudo systemctl status port-forward@default-datacollector-3000-3000.service
# ./start-port-forward.sh qdrant qdrant 6334 6334
# ./start-port-forward.sh qdrant qdrant 6333 6333