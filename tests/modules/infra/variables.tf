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

variable "app_wildcard" {
  type        = string
  default     = "manage"
  description = "Subdomain for CNAME wildcard for applicaitons"
}

variable "rancher_domain" {
  type        = string
  default     = "manage"
  description = "Rancher manager UI subdomain"
}

# Number of worker nodes
variable "worker_node_count" {
  type        = number
  default     = 3
  description = "Number of worker nodes to provision"
}

# Admin User
variable "node_admin_user" {
  type        = string
  default     = "admin"
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

# SSH Port
variable "node_ssh_port" {
  type        = number
  default     = 22
  description = "Port to use for ssh conneciton to nodes"

}

# Base image to use
variable "node_base_image" {
  type        = string
  default     = "Ubuntu Bionic"
  description = "Base image for node"
}

variable "node_image_architechure" {
  type        = string
  default     = "x86_64"
  description = "Architecture for image"
}

variable "node_type" {
  type        = string
  default     = "C2S"
  description = "VM type for nodes"
}

variable "node_domain" {
  type        = string
  default     = "nodes"
  description = "Node subdomain"
}

variable "cloudflare_email" {
  type        = string
  default     = "mail@exaple.com"
  description = "Email for cloudflare account"
}

variable "cloudflare_token" {
  type        = string
  default     = "change_me"
  description = "API Token for cloudflare"
}

variable "scaleway_org" {
  type        = string
  description = "Scaleway orginization"
}

variable "scaleway_token" {
  type        = string
  description = "Scaleway API token"
}

variable "scaleway_region" {
  type        = string
  description = "Scaleway region"
}
