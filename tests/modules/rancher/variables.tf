variable "worker_public_ips" {
  type        = list(string)
  description = "Worker node ip addresses"
}

variable "worker_private_ips" {
  type        = list(string)
  description = "Worker node ip addresses"
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

# SSH Port
variable "node_ssh_port" {
  type        = number
  default     = 22
  description = "Port to use for ssh conneciton to nodes"

}

# Admin User
variable "node_admin_user" {
  type        = string
  default     = "tmac"
  description = "Name of the created admin user."
}

# Path to ssh private key
variable "ssh_priv_key_path" {
  type        = string
  default     = "~/.ssh/id_rsa"
  description = "Path to ssh private key for provisioning"
}

# Path to ssh public key
variable "ssh_pub_key_path" {
  type        = string
  default     = "~/.ssh/id_rsa.pub"
  description = "Path to ssh public key for provisioning"
}

variable "rancher_access_key" {
  type = string
}

variable "rancher_secret_key" {
  type = string
}