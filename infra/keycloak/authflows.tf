# Modify the default browser flow to redirect to the CMU SAML provider
resource "keycloak_authentication_flow" "browser" {
  realm_id    = keycloak_realm.labrador.id
  alias       = "browser"
  description = "Browser based authentication"
}

resource "keycloak_authentication_execution" "saml_redirector" {
  realm_id          = keycloak_realm.labrador.id
  parent_flow_alias = "browser"
  authenticator     = "identity-provider-redirector"
  requirement       = "REQUIRED"
  priority          = 25
}


resource "keycloak_authentication_execution_config" "saml_redirector_config" {
  realm_id     = keycloak_realm.labrador.id
  execution_id = keycloak_authentication_execution.saml_redirector.id
  alias        = "CMU SAML Redirector"
  config = {
    defaultProvider = "cmu-saml"
  }
}

# Auto-link LDAP users flow
resource "keycloak_authentication_flow" "auto_link_ldap_users" {
  realm_id    = keycloak_realm.labrador.id
  alias       = "Auto-link LDAP users"
  description = "Actions taken after first broker login with identity provider account, which is not yet linked to any Keycloak account"
}


# Results in "Invalid username or password." error when this execution is disabled
resource "keycloak_authentication_execution" "create_user_if_unique" {
  realm_id          = keycloak_realm.labrador.id
  parent_flow_alias = "Auto-link LDAP users"
  authenticator     = "idp-create-user-if-unique"
  requirement       = "ALTERNATIVE"
  priority          = 0
}

resource "keycloak_authentication_execution" "auto_set_existing_user" {
  realm_id          = keycloak_realm.labrador.id
  parent_flow_alias = "Auto-link LDAP users"
  authenticator     = "idp-auto-link"
  requirement       = "ALTERNATIVE"
  priority          = 1
}
