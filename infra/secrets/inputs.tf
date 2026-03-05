variable "admin_group_name" {
  description = "Admin group name"
  type        = string
}

variable "keycloak_realm_url" {
  description = "Keycloak realm URL"
  type        = string
  default     = "https://idp.scottylabs.org/realms/labrador"
}

variable "oidc_client_id" {
  description = "OIDC client ID"
  type        = string
}

variable "oidc_client_secret" {
  description = "OIDC client secret"
  type        = string
  sensitive   = true
}

variable "secrets_url" {
  description = "Secrets URL"
  type        = string
}


variable "vault_token" {
  description = "Vault token"
  type        = string
  sensitive   = true
}

