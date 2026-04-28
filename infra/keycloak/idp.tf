# GitHub IDP
resource "keycloak_oidc_github_identity_provider" "github_idp" {
  realm         = keycloak_realm.labrador.realm
  alias         = "github"
  display_name  = "GitHub"
  client_id     = var.github_client_id
  client_secret = var.github_client_secret
}
