resource "local_file" "kubeconfig" {
  filename = "${path.module}/../kubeconf"
  content  = "${var.kubeconfig}"
}
