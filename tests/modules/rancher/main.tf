provider "rancher2" {
  api_url    = "https://${var.rancher_domain}.${var.admin_wildcard}.${var.root_domain}"
  access_key = "${var.rancher_access_key}"
  secret_key = "${var.rancher_secret_key}"
}

data "local_file" "ssh_priv_key" {
  filename = "${path.module}/${var.ssh_priv_key_path}"
}

data "local_file" "ssh_pub_key" {
  filename = "${path.module}/${var.ssh_pub_key_path}"
}

resource "rancher2_cluster" "nimbus" {
  name        = "nimbus"
  description = "tmacs.cloud application cluster"
  rke_config {
    network {
      plugin = "canal"
    }
  }
}

resource "null_resource" "init_nodes" {
  depends_on = [rancher2_cluster.nimbus]
  count      = 3
  connection {
    host        = "${var.worker_public_ips[count.index]}"
    user        = "${var.node_admin_user}"
    port        = "${var.node_ssh_port}"
    private_key = "${data.local_file.ssh_priv_key.content}"
  }

  provisioner "remote-exec" {
    inline = [
      "${rancher2_cluster.nimbus.cluster_registration_token[0].node_command} --etcd --worker --controlplane --address ${var.worker_public_ips[count.index]} --internal-address ${var.worker_private_ips[count.index]}"
    ]
  }
}
