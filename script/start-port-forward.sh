#!/usr/bin/env bash

# 假設這隻腳本叫 start-port-forward.sh

if [ -z "$1" ]; then
#  NAMESPACE-SERVICENAME-HOSTPORT-CONTAINERPORT
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
sudo systemctl enable port-forward@$NAMESPACE-$SERVICE_NAME-$HOST_PORT-$CONTAINER_PORT.service
sudo systemctl start port-forward@$NAMESPACE-$SERVICE_NAME-$HOST_PORT-$CONTAINER_PORT.service
sudo systemctl status port-forward@$NAMESPACE-$SERVICE_NAME-$HOST_PORT-$CONTAINER_PORT.service