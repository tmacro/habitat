
output "worker_public_ips" {
  value = "${scaleway_server.worker[*].public_ip}"
}

output "worker_private_ips" {
  value = "${scaleway_server.worker[*].private_ip}"
}

output "manager_public_ip" {
  value = "${scaleway_server.manager.public_ip}"
}

output "manager_private_ip" {
  value = "${scaleway_server.manager.private_ip}"
}

output "manager_hostname" {
  value = "${cloudflare_record.rancher_admin.hostname}"
}