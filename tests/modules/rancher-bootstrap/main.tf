provider "rancher2" {
  api_url   = "https://${var.rancher_domain}.${var.admin_wildcard}.${var.root_domain}"
  bootstrap = true
}

# Create a new rancher2 Bootstrap
resource "rancher2_bootstrap" "admin" {
  password  = "${var.default_admin_password}"
  telemetry = true
}
