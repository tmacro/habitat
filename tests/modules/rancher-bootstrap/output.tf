output "rancher_access_key" {
  value = "${rancher2_bootstrap.admin.token_id}"
}

output "rancher_secret_key" {
  value = "${split(":", rancher2_bootstrap.admin.token)[1]}"
}

