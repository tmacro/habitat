
variable "kube_config_path" {
  type        = string
  description = "Path to kubectl config file"
}

variable "rancher_project_id" {
  type        = string
  description = "Default rancher cluster project id"
}

variable "rancher_access_key" {
  type = string
}

variable "rancher_secret_key" {
  type = string
}

variable "root_domain" {
  type        = string
  description = "Root domain name"
}

variable "keycloak_domain" {
  type        = string
  description = "Keycloak admin domain name"
}

variable "longhorn_domain" {
  type        = string
  description = "Keycloak admin domain name"
}

variable "keycloak_realm" {
  type        = string
  description = "Keycloak realm name"
}

variable "admin_wildcard" {
  type        = string
  description = "CNAME wildcard for admin services"
}

variable "rancher_domain" {
  type        = string
  default     = "rancher"
  description = "Rancher manager UI subdomain"
}

variable "cloudflare_token" {
  type = string
}

variable "cloudflare_email" {
  type = string
}

variable "default_admin_email" {
  type = string
}

variable "default_admin_user" {
  type = string
}

variable "default_admin_password" {
  type = string
}

variable "release_name" {
  type        = string
  description = "Keycloak realm name"
  default     = "nimbus"
}
