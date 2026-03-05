module "keycloak" {
  source                   = "./keycloak"
  admin_group_suffix       = local.admin_suffix
  leadership_group_name    = local.leadership_group_name
  leadership_data          = local.leadership_data
  cmu_ldap_bind_credential = var.cmu_ldap_bind_credential
  keycloak_client_id       = var.keycloak_client_id
  keycloak_client_secret   = var.keycloak_client_secret
  keycloak_realm_url       = local.keycloak_realm_url
  openbao_oidc_client_id   = local.openbao_oidc_client_id
  secrets_url              = local.secrets_url
}

module "secrets" {
  source                = "./secrets"
  admin_group_suffix    = local.admin_suffix
  leadership_group_name = local.leadership_group_name
  vault_token           = var.vault_token
  oidc_client_secret    = module.keycloak.openbao_oidc_client_secret
  oidc_client_id        = local.openbao_oidc_client_id
  keycloak_realm_url    = local.keycloak_realm_url
  secrets_url           = local.secrets_url
}
