resource "scaleway_ip" "worker" {
  count = "${var.worker_node_count}"
}

resource "scaleway_server" "worker" {
  name      = "nimbus-worker-${count.index}"
  image     = "${data.scaleway_image.node.id}"
  type      = "${var.node_type}"
  cloudinit = "${data.template_file.cloud_init.rendered}"
  public_ip = "${scaleway_ip.worker[count.index].ip}"
  count     = "${var.worker_node_count}"

  connection {
    host        = "${scaleway_ip.worker[count.index].ip}"
    private_key = "${local.ssh_priv_key}"
  }

  provisioner "remote-exec" {
    script = "${path.module}/conf/wait-for-cloud-init"
  }

  provisioner "file" {
    source      = "${path.module}/conf/common/50-unattended-upgrades"
    destination = "/etc/apt/apt.conf.d/50unattended-upgrades"
  }
}


resource "null_resource" "worker_iptables" {
  count      = 3
  depends_on = [scaleway_server.worker]
  connection {
    host        = "${scaleway_ip.worker[count.index].ip}"
    private_key = "${local.ssh_priv_key}"
  }

  provisioner "remote-exec" {
    inline = [
      "mkdir -p /opt/setup/iptables",
      "mkdir -p /etc/iptables",
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
      # Public Node IPs
      %{for ip in scaleway_server.worker[*].public_ip}
      -A UDP -p udp --dport 4789 -s ${ip} -j ACCEPT
      -A UDP -p udp --dport 8472 -s ${ip} -j ACCEPT
      -A UDP -p udp --dport 30000:32767 -s ${ip} -j ACCEPT
      %{endfor}

      %{for ip in scaleway_server.worker[*].private_ip}
      -A UDP -p udp --dport 4789 -s ${ip} -j ACCEPT
      -A UDP -p udp --dport 8472 -s ${ip} -j ACCEPT
      -A UDP -p udp --dport 30000:32767 -s ${ip} -j ACCEPT
      %{endfor}

      # Acceptable TCP traffic
      -A TCP -p tcp --dport ${var.node_ssh_port} -j ACCEPT
      -A TCP -p tcp --dport 80 -j ACCEPT
      -A TCP -p tcp --dport 443 -j ACCEPT
      -A TCP -p tcp --dport 2376   -j ACCEPT
      -A TCP -p tcp --dport 6443   -j ACCEPT

      # Public Node IPs
      %{for ip in scaleway_server.worker[*].public_ip}
      -A TCP -p tcp --dport 2379:2380 -s ${ip} -j ACCEPT
      -A TCP -p tcp --dport 10250:10252 -s ${ip} -j ACCEPT
      -A TCP -p tcp --dport 10256 -s ${ip} -j ACCEPT
      -A TCP -p tcp --dport 30000:32767 -s ${ip} -j ACCEPT
      %{endfor}

      #Private Node IPs
      %{for ip in scaleway_server.worker[*].private_ip}
      -A TCP -p tcp --dport 2379:2380 -s ${ip} -j ACCEPT
      -A TCP -p tcp --dport 10250:10252 -s ${ip} -j ACCEPT
      -A TCP -p tcp --dport 10256 -s ${ip} -j ACCEPT
      -A TCP -p tcp --dport 30000:32767 -s ${ip} -j ACCEPT
      %{endfor}
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
    script = "${path.module}/conf/setup-worker.sh"
  }
}
