resource "keycloak_realm" "labrador" {
  realm                       = "labrador"
  default_signature_algorithm = "RS256"
}

# Client that handles OIDC login in OpenBao
# Reference: https://medium.com/@sauravkumarsct/integrate-keycloak-as-oidc-jwt-provider-with-hashicorp-vault-ae9ebcf8e335
resource "keycloak_openid_client" "openbao" {
  realm_id  = keycloak_realm.labrador.id
  client_id = "openbao"

  name        = "OpenBao"
  description = "Secrets manager for Labrador"

  access_type = "CONFIDENTIAL"

  root_url = "https://bao.scottylabs.org/ui/vault/auth/oidc/oidc/callback"
  valid_redirect_uris = [
    "https://bao.scottylabs.org/oidc/callback",
    "https://bao.scottylabs.org/ui/vault/auth/oidc/oidc/callback",
    "http://localhost:8250/oidc/callback"
  ]
  web_origins = ["https://bao.scottylabs.org"]
  admin_url   = "https://bao.scottylabs.org/ui/vault/auth/oidc/oidc/callback"

  standard_flow_enabled    = true
  service_accounts_enabled = true

  frontchannel_logout_enabled = true
}
