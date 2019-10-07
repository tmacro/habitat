provider "hcloud" {
  token = "${var.hcloud_token}"
}

resource "hcloud_floating_ip" "manager" {
  type  = "ipv4"
  count = "${var.manager_count}"
}

resource "hcloud_floating_ip" "worker" {
  type  = "ipv4"
  count = "${var.worker_count}"
}

resource "hcloud_server" "manager" {
  name        = "nimbus-manager-${count.index}"
  image       = "${var.manager_base_image}"
  server_type = "${var.manager_machine_type}"
  location    = "${var.hcloud_region}"
  user_date   = "${var.manager_cloud_init ? var.manager_cloud_init : null}"
  count       = "${var.manager_count}"
}

resource "hcloud_server" "worker" {
  name        = "nimbus-worker-${count.index}"
  image       = "${var.worker_base_image}"
  server_type = "${var.worker_machine_type}"
  location    = "${var.hcloud_region}"
  user_date   = "${var.worker_cloud_init ? var.worker_cloud_init : null}"
  count       = "${var.worker_count}"
}

resource "hcloud_floating_ip_assignment" "manager" {
  floating_ip_id = "${hcloud_floating_ip.manager[count.index].id}"
  server_id      = "${hcloud_server.manager[count.index].id}"
  count          = "${var.manager_count}"
}

resource "hcloud_floating_ip_assignment" "worker" {
  floating_ip_id = "${hcloud_floating_ip.worker[count.index].id}"
  server_id      = "${hcloud_server.worker[count.index].id}"
  count          = "${var.worker_count}"
}
