kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

VERSION=$(curl -L -s https://raw.githubusercontent.com/argoproj/argo-cd/stable/VERSION)
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/download/v$VERSION/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64

argocd login --core

sudo vim /etc/systemd/system/argocd-port-forward.service

[Unit]
Description=ArgoCD Port-Forward Service
After=minikube.service
Requires=minikube.service

[Service]
Type=simple
ExecStart=/usr/local/bin/minikube kubectl -- port-forward --address 0.0.0.0 svc/argocd-server -n argocd 8080:80
Restart=always
RestartSec=5s  # Wait 5 seconds before restarting
StartLimitInterval=300
StartLimitBurst=5
User=jackyli
Group=jackyli
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

sudo systemctl daemon-reload
sudo systemctl enable argocd-port-forward.service
sudo systemctl start argocd-port-forward.service
sudo systemctl status argocd-port-forward.service


argocd admin initial-password -n argocd

argocd --insecure login localhost:8080

argocd account update-password

export CLUSTER_CONFIG_PROJECT_URL=git@github.com:meowalien/discovery_system.git

argocd repo add $CLUSTER_CONFIG_PROJECT_URL --ssh-private-key-path ~/argocd_ssh_key


#ls /etc/systemd/system/multi-user.target.wants/