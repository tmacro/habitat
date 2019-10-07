variable "default_admin_password" {
  type        = string
  default     = "change_me"
  description = "Password for the Rancher UI admin user"
}

variable "root_domain" {
  type        = string
  default     = "example.com"
  description = "Root domain for deployment"
}

variable "admin_wildcard" {
  type        = string
  default     = "manage"
  description = "Subdomain for CNAME wildcard for administration"
}

variable "rancher_domain" {
  type        = string
  default     = "manage"
  description = "Rancher manager UI subdomain"
}