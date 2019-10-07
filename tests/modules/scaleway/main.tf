provider "scaleway" {
  organization = "${var.scaleway_org}"
  token        = "${var.scaleway_token}"
  region       = "${var.scaleway_region}"
}

data "scaleway_image" "manager" {
  architecture = "${var.manager_image_architechure}"
  name         = "${var.manager_base_image}"
}

data "scaleway_image" "worker" {
  architecture = "${var.worker_image_architechure}"
  name         = "${var.worker_base_image}"
}

resource "scaleway_ip" "manager" {
  count = "${var.manager_count}"
}

resource "scaleway_ip" "worker" {
  count = "${var.worker_count}"
}

resource "scaleway_server" "manager" {
  name      = "nimbus-manager-${count.index}"
  image     = "${data.scaleway_image.manager.id}"
  type      = "${var.manager_machine_type}"
  cloudinit = "${var.manager_cloud_init ? var.manager_cloud_init : null}"
  public_ip = "${scaleway_ip.manager[count.index].ip}"
  count     = "${var.manager_count}"
}

resource "scaleway_server" "worker" {
  name      = "nimbus-worker-${count.index}"
  image     = "${data.scaleway_image.worker.id}"
  type      = "${var.worker_machine_type}"
  cloudinit = "${var.worker_cloud_init ? var.worker_cloud_init : null}"
  public_ip = "${scaleway_ip.worker[count.index].ip}"
  count     = "${var.worker_count}"
}