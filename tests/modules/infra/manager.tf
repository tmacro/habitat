resource "scaleway_ip" "manager" {}

resource "scaleway_server" "manager" {
  name      = "nimbus-manager"
  image     = "${data.scaleway_image.node.id}"
  type      = "${var.node_type}"
  cloudinit = "${data.template_file.cloud_init.rendered}"
  public_ip = "${scaleway_ip.manager.ip}"

  connection {
    host        = "${scaleway_ip.manager.ip}"
    private_key = "${local.ssh_priv_key}"
  }

  provisioner "remote-exec" {
    script = "${path.module}/conf/wait-for-cloud-init"
  }

  provisioner "file" {
    destination = "/etc/systemd/system/rancher-manager.service"
    content     = <<-EOT
      [Unit]
      Description=Rancher Control Plane
      After=docker.service
      Requires=docker.service
      Conflicts=rancher-backup.service

      [Service]
      TimeoutStartSec=0
      Restart=always
      ExecStartPre=-/usr/bin/docker stop rancher-manager
      ExecStartPre=-/usr/bin/docker create --name rancher-data -v /opt/rancher/data:/var/lib/rancher -v /opt/rancher/auditlog:/var/log/auditlog alpine
      ExecStartPre=-/usr/bin/docker rm rancher-manager
      ExecStartPre=/usr/bin/docker pull rancher/rancher:latest
      ExecStart=/usr/bin/docker run --rm --name rancher-manager -p 80:80 -p 443:443 -e AUDIT_LEVEL=1 --volumes-from rancher-data rancher/rancher:latest --acme-domain ${var.manager_hostname}

      [Install]
      WantedBy=multi-user.target
    EOT
  }

  provisioner "file" {
    source      = "${path.module}/conf/manager/rancher-backup.service"
    destination = "/etc/systemd/system/rancher-backup.service"
  }

  provisioner "file" {
    source      = "${path.module}/conf/manager/rancher-backup.timer"
    destination = "/etc/systemd/system/rancher-backup.timer"
  }

  provisioner "file" {
    source      = "${path.module}/conf/manager/rancher-manager-restart.timer"
    destination = "/etc/systemd/system/rancher-manager-restart.timer"
  }

  provisioner "file" {
    source      = "${path.module}/conf/manager/backup-rancher.sh"
    destination = "/etc/systemd/system/backup-rancher.sh"
  }

  provisioner "file" {
    source      = "${path.module}/conf/common/50-unattended-upgrades"
    destination = "/etc/apt/apt.conf.d/50unattended-upgrades"
  }

  provisioner "remote-exec" {
    inline = [
      "mkdir -p /opt/setup/iptables",
    ]
  }

  provisioner "file" {
    source      = "${path.module}/conf/firewall/common.v6"
    destination = "/opt/setup/iptables/rules.v6"
  }


  provisioner "file" {
    destination = "/opt/setup/iptables/rules.v4"
    content     = <<-EOT
      *filter
      # Allow all outgoing, but drop incoming and forwarding packets by default
      :INPUT DROP [0:0]
      :FORWARD DROP [0:0]
      :OUTPUT ACCEPT [0:0]

      # Custom per-protocol chains
      :UDP - [0:0]
      :TCP - [0:0]
      :ICMP - [0:0]

      # Acceptable UDP traffic

      # Acceptable TCP traffic
      -A TCP -p tcp --dport ${var.node_ssh_port} -j ACCEPT
      -A TCP -p tcp --dport 80 -j ACCEPT
      -A TCP -p tcp --dport 443 -j ACCEPT

      # Acceptable ICMP traffic

      # Boilerplate acceptance policy
      -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
      -A INPUT -i lo -j ACCEPT

      # Drop invalid packets
      -A INPUT -m conntrack --ctstate INVALID -j DROP

      # Pass traffic to protocol-specific chains
      ## Only allow new connections (established and related should already be handled)
      ## For TCP, additionally only allow new SYN packets since that is the only valid
      ## method for establishing a new TCP connection
      -A INPUT -p udp -m conntrack --ctstate NEW -j UDP
      -A INPUT -p tcp --syn -m conntrack --ctstate NEW -j TCP
      -A INPUT -p icmp -m conntrack --ctstate NEW -j ICMP

      # Reject anything that's fallen through to this point
      ## Try to be protocol-specific w/ rejection message
      -A INPUT -p udp -j REJECT --reject-with icmp-port-unreachable
      -A INPUT -p tcp -j REJECT --reject-with tcp-reset
      -A INPUT -j REJECT --reject-with icmp-proto-unreachable

      # Commit the changes
      COMMIT

      *raw
      :PREROUTING ACCEPT [0:0]
      :OUTPUT ACCEPT [0:0]
      COMMIT

      *nat
      :PREROUTING ACCEPT [0:0]
      :INPUT ACCEPT [0:0]
      :OUTPUT ACCEPT [0:0]
      :POSTROUTING ACCEPT [0:0]
      COMMIT

      *security
      :INPUT ACCEPT [0:0]
      :FORWARD ACCEPT [0:0]
      :OUTPUT ACCEPT [0:0]
      COMMIT

      *mangle
      :PREROUTING ACCEPT [0:0]
      :INPUT ACCEPT [0:0]
      :FORWARD ACCEPT [0:0]
      :OUTPUT ACCEPT [0:0]
      :POSTROUTING ACCEPT [0:0]
      COMMIT
    EOT
  }

  provisioner "file" {
    content     = "${data.template_file.sshd_config.rendered}"
    destination = "/etc/ssh/sshd_config"
  }

  provisioner "remote-exec" {
    script = "${path.module}/conf/setup-manager.sh"
  }
}
