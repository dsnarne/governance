# Reference: https://medium.com/@sauravkumarsct/integrate-keycloak-as-oidc-jwt-provider-with-hashicorp-vault-ae9ebcf8e335

resource "vault_auth_backend" "oidc" {
  type        = "oidc"
  description = "OIDC via Keycloak"
}

resource "vault_generic_endpoint" "oidc_config" {
  path = "auth/${vault_auth_backend.oidc.path}/config"

  data_json = jsonencode({
    oidc_client_id     = "openbao"
    oidc_client_secret = var.oidc_client_secret
    default_role       = "default"
    oidc_discovery_url = "https://idp.scottylabs.org/realms/labrador"
  })
}

resource "vault_generic_endpoint" "oidc_role_default" {
  path = "auth/${vault_auth_backend.oidc.path}/role/default"

  data_json = jsonencode({
    user_claim              = "sub"
    token_policies          = ["default"]
    role_type               = "oidc"
    token_ttl               = "10m"
    token_no_default_policy = true
    token_type              = "service"
    groups_claim            = "groups"
    allowed_redirect_uris = [
      "https://bao.scottylabs.org/ui/vault/auth/oidc/oidc/callback",
      "http://localhost:8250/oidc/callback",
    ]
  })
}
