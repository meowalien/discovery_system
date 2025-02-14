
sudo vim /etc/systemd/system/minikube.service

[Unit]
Description=Minikube Start Service
After=network.target docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/minikube start --driver=docker
ExecStop=/usr/local/bin/minikube stop
RemainAfterExit=true
User=jackyli
Group=jackyli
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target



sudo systemctl daemon-reload
sudo systemctl enable minikube.service
sudo systemctl start minikube.service
sudo systemctl status minikube.service

