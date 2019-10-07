
# Terraform module for deploying the tmacs.cloud infrastructure and applications

# Declare our highlevel providers


provider "cloudflare" {
  email = "${var.cloudflare_email}"
  token = "${var.cloudflare_token}"
}

provider "scaleway" {
  organization = "${var.scaleway_org}"
  token        = "${var.scaleway_token}"
  region       = "${var.scaleway_region}"
}

data "local_file" "ssh_priv_key" {
  filename = "${var.ssh_priv_key_path}"
}

data "local_file" "ssh_pub_key" {
  filename = "${var.ssh_pub_key_path}"
}

data "template_file" "cloud_init" {
  template = "${file("${path.module}/conf/cloud-init.yaml.tpl")}"
  vars = {
    ssh_pub_key = "${local.ssh_pub_key}"
    admin_user  = "${var.node_admin_user}"
  }
}

data "template_file" "sshd_config" {
  template = "${file("${path.module}/conf/common/sshd_config.tpl")}"
  vars = {
    sshd_port  = "${var.node_ssh_port}"
    admin_user = "${var.node_admin_user}"
  }
}

data "scaleway_image" "node" {
  architecture = "${var.node_image_architechure}"
  name         = "${var.node_base_image}"
}

locals {
  manager_hostname = "${var.rancher_domain}.${var.admin_wildcard}.${var.root_domain}"
  ssh_priv_key     = "${data.local_file.ssh_priv_key.content}"
  ssh_pub_key      = "${data.local_file.ssh_pub_key.content}"
}