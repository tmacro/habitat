#!/bin/sh


_setup_iptables() {
    echo "Applying iptables rules..."
    cp -v /opt/setup/iptables/* /etc/iptables
    iptables-restore < /etc/iptables/rules.v4
    # ip6tables-restore < /etc/iptables/rules.v6
    systemctl restart docker
    echo "Finished applying iptables rules!"
}

_setup_rancher() {
    echo "Starting rancher manager..."
    systemctl enable rancher-manager.service
    systemctl start rancher-manager.service
    echo "Rancher manager started!"
}

_setup_backup() {
    echo "Starting rancher manager backup timer..."
    systemctl enable rancher-backup.timer
    systemctl start rancher-backup.timer
    echo "Rancher manager backup timer running!"
}

echo -n "Reloading systemd..."
systemctl daemon-reload
echo "Done!"

_setup_iptables
_setup_rancher
_setup_backup

echo "Restarting sshd..."
systemctl restart sshd
echo "Done!"