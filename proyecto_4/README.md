Proyecto Final Documentación:

Comandos nodo master:
sudo snap install microk8s --classic

sudo microk8s enable dns storage ingress

sudo usermod -a -G microk8s $USER
newgrp microk8s
