module "keycloak" {
  source                 = "./keycloak"
  keycloak_client_id     = var.keycloak_client_id
  keycloak_client_secret = var.keycloak_client_secret
  keycloak_url           = var.keycloak_url
  keycloak_realm         = var.keycloak_realm
}

module "secrets" {
  source             = "./secrets"
  vault_token        = var.vault_token
  oidc_client_secret = module.keycloak.oidc_client_secret
}
