variable "vault_token" {
  description = "Vault token"
  type        = string
  sensitive   = true
}

variable "oidc_client_secret" {
  description = "OIDC client secret"
  type        = string
  sensitive   = true
}
