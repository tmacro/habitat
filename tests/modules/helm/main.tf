
#
# Setup Providers
#

provider "helm" {
  kubernetes {
    config_path = "${var.kube_config_path}"
  }

  service_account = "tiller"
}

provider "rancher2" {
  api_url    = "https://${var.rancher_domain}.${var.admin_wildcard}.${var.root_domain}"
  access_key = "${var.rancher_access_key}"
  secret_key = "${var.rancher_secret_key}"
}

provider "kubernetes" {
  config_path = "${var.kube_config_path}"
}

#
# Setup Helm Repository
#

data "helm_repository" "nimbus" {
  name = "nimbus"
  url  = "http://127.0.0.1:8879/charts"
  # url  = "https://tmacro.github.io/charts/"
}

#
# Setup namespaces
#

resource "rancher2_namespace" "longhorn_system" {
  name        = "longhorn-system"
  project_id  = "${var.rancher_project_id}"
  description = "Longhorn namespace"
}

resource "rancher2_namespace" "nimbus" {
  name        = "nimbus"
  project_id  = "${var.rancher_project_id}"
  description = "nimbus application namespace"
}

locals {
  cert_manager_labels = {
    "certmanager.k8s.io/disable-validation" = true
  }
}

resource "rancher2_namespace" "cert_manager" {
  name        = "cert-manager"
  project_id  = "${var.rancher_project_id}"
  description = "cert-manager namespace"
  labels      = local.cert_manager_labels
}

#
# Install cert-manager
#

resource "null_resource" "cert_manager_crds" {
  depends_on = [rancher2_namespace.cert_manager]

  # Install crds
  provisioner "local-exec" {
    command = "kubectl apply --kubeconfig ${var.kube_config_path} -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.9/deploy/manifests/00-crds.yaml"
  }
}

resource "helm_release" "cert_manager" {
  depends_on = [null_resource.cert_manager_crds]
  name       = "cert-manager"
  namespace  = "cert-manager"
  repository = "${data.helm_repository.nimbus.metadata.0.name}"
  chart      = "nimbus/cert-manager"
  version    = "v0.1.0"

  set {
    name  = "letsencryptEmail"
    value = "${var.default_admin_email}"
  }

  set {
    name  = "cloudflareEmail"
    value = "${var.cloudflare_email}"
  }

  set_sensitive {
    name  = "cloudflareApiKey"
    value = "${var.cloudflare_token}"
  }
}


#
# Install longhorn
#

data "template_file" "longhorn_values" {
  template = "${file("${path.module}/values/longhorn.yaml")}"
  vars = {
    longhorn_domain = "${var.longhorn_domain}"
    root_domain     = "${var.root_domain}"
    admin_wildcard  = "${var.admin_wildcard}"
    release_name    = "${var.release_name}"
  }
}

resource "helm_release" "longhorn" {
  depends_on = [rancher2_namespace.longhorn_system, helm_release.cert_manager]
  name       = "longhorn"
  repository = "${data.helm_repository.nimbus.metadata.0.name}"
  chart      = "nimbus/longhorn"
  namespace  = "longhorn-system"
  wait       = true
  timeout    = 1800
  recreate_pods = true

  set {
    name  = "service.ui.type"
    value = "ClusterIP"
  }

  values = [
    "${data.template_file.longhorn_values.rendered}",
  ]
}

#
# Install nimbus application stack
#

data "template_file" "nimbus_keycloak_values" {
  template = "${file("${path.module}/values/keycloak.yaml")}"
  vars = {
    keycloak_realm         = "${var.keycloak_realm}"
    keycloak_domain        = "${var.keycloak_domain}"
    root_domain            = "${var.root_domain}"
    admin_wildcard         = "${var.admin_wildcard}"
    default_admin_user     = "${var.default_admin_user}"
    default_admin_password = "${var.default_admin_password}"
    release_name           = "${var.release_name}"
  }
}

data "template_file" "nimbus_oauth2_proxy_values" {
  template = "${file("${path.module}/values/oauth2-proxy.yaml")}"
  vars = {
    keycloak_realm  = "${var.keycloak_realm}"
    keycloak_domain = "${var.keycloak_domain}"
    root_domain     = "${var.root_domain}"
    admin_wildcard  = "${var.admin_wildcard}"
    release_name    = "${var.release_name}"
    longhorn_domain        = "${var.longhorn_domain}"
  }
}

resource "helm_release" "nimbus" {
  depends_on = [helm_release.longhorn, helm_release.cert_manager, rancher2_namespace.nimbus]
  name       = "nimbus"
  namespace  = "nimbus"
  repository = "${data.helm_repository.nimbus.metadata.0.name}"
  chart      = "nimbus/nimbus"
  version    = "0.1.0"
  recreate_pods = true
  values = [
    "${data.template_file.nimbus_keycloak_values.rendered}",
    "${data.template_file.nimbus_oauth2_proxy_values.rendered}"
  ]

}