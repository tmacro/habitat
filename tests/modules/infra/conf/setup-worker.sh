#!/bin/sh


_setup_iptables() {
    echo "Applying iptables rules..."
    cp -v /opt/setup/iptables/* /etc/iptables
    iptables-restore < /etc/iptables/rules.v4
    # ip6tables-restore < /etc/iptables/rules.v6
    systemctl restart docker
    echo "Finished applying iptables rules!"
}

echo -n "Reloading systemd..."
systemctl daemon-reload
echo "Done!"

_setup_iptables

echo "Restarting sshd..."
systemctl restart sshd
echo "Done!"