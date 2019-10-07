
output "kubeconfig" {
  value = "${rancher2_cluster.nimbus.kube_config}"
}

output "rancher_project_id" {
  value = "${rancher2_cluster.nimbus.default_project_id}"
}
