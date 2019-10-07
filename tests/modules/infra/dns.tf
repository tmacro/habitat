resource "cloudflare_record" "rancher_admin" {
  domain = "${var.root_domain}"
  name   = "${var.rancher_domain}.${var.admin_wildcard}"
  value  = "${scaleway_server.manager.public_ip}"
  type   = "A"
  ttl    = 1
}

resource "cloudflare_record" "nodes_group" {
  domain = "${var.root_domain}"
  name   = "${var.node_domain}"
  value  = "${scaleway_server.worker[count.index].public_ip}"
  type   = "A"
  ttl    = 1
  count  = 3
}

resource "cloudflare_record" "nodes_individual" {
  domain = "${var.root_domain}"
  name   = "${count.index}.${var.node_domain}"
  value  = "${scaleway_server.worker[count.index].public_ip}"
  type   = "A"
  ttl    = 1
  count  = 3
}

resource "cloudflare_record" "admin_wildcard" {
  domain = "${var.root_domain}"
  name   = "*.${var.admin_wildcard}"
  value  = "${var.node_domain}.${var.root_domain}"
  type   = "CNAME"
  ttl    = 1
}

resource "cloudflare_record" "app_wildcard" {
  domain = "${var.root_domain}"
  name   = "*.${var.app_wildcard}"
  value  = "${var.node_domain}.${var.root_domain}"
  type   = "CNAME"
  ttl    = 1
}