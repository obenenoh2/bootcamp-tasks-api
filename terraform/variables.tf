variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "staging"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "centralus"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "kingsly"
}

variable "db_username" {
  description = "Database administrator username"
  type        = string
  default     = "kingslyadmin"
}

variable "db_password" {
  description = "Database administrator password"
  type        = string
  sensitive   = true
}

variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
  sensitive   = true
}
