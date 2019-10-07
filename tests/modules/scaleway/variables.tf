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

# Number of worker nodes
variable "worker_count" {
  type        = number
  default     = 3
  description = "Number of worker nodes to provision"
}

variable "manager_count" {
  type        = number
  default     = 1
  description = "Number of manager nodes to provision"
}

# Admin User
variable "admin_user" {
  type        = string
  default     = "admin"
  description = "Name of the created admin user."
}

variable "ssh_priv_key" {
  type        = string
  description = "Private key for server administration"
}

variable "ssh_pub_key" {
  type        = string
  description = "Public key to install on created servers"
}

# Base image to use
variable "worker_base_image" {
  type        = string
  default     = "Ubuntu Bionic"
  description = "Base image for workers"
}

variable "worker_image_architechure" {
  type        = string
  default     = "x86_64"
  description = "Architecture for worker images"
}

variable "worker_machine_type" {
  type        = string
  default     = "C2S"
  description = "VM type for workers"
}

variable "worker_cloud_init" {
  type        = string
  default     = ""
  description = "cloud-init for workers"
}

variable "manager_base_image" {
  type        = string
  default     = "Ubuntu Bionic"
  description = "Base image for managers"
}

variable "manager_image_architechure" {
  type        = string
  default     = "x86_64"
  description = "Architecture for manager images"
}

variable "manager_machine_type" {
  type        = string
  default     = "C2S"
  description = "VM type for managers"
}

variable "manager_cloud_init" {
  type        = string
  default     = ""
  description = "cloud-init for managers"
}