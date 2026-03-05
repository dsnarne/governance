variable "admin_group_suffix" {
  description = "Admin group suffix"
  type        = string
}

variable "cmu_ldap_bind_credential" {
  description = "CMU LDAP bind password"
  type        = string
  sensitive   = true
}

variable "leadership_group_name" {
  description = "Leadership group name"
  type        = string
}

variable "leadership_data" {
  description = "Leadership data"
  type = object({
    members = list(string)
    admins  = list(string)
  })
}

variable "keycloak_client_id" {
  description = "Keycloak client ID"
  type        = string
  sensitive   = true
}

variable "keycloak_client_secret" {
  description = "Keycloak client secret"
  type        = string
  sensitive   = true
}

variable "keycloak_realm" {
  description = "Keycloak realm"
  type        = string
  default     = "labrador"
}

variable "keycloak_realm_url" {
  description = "Keycloak realm URL"
  type        = string
}

variable "keycloak_url" {
  description = "Keycloak URL"
  type        = string
  default     = "https://idp.scottylabs.org"
}

variable "openbao_oidc_client_id" {
  description = "OIDC client ID"
  type        = string
}

variable "secrets_url" {
  description = "Secrets URL"
  type        = string
}

