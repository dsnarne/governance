resource "keycloak_ldap_user_federation" "cmu_ldap" {
  # General options
  realm_id = keycloak_realm.labrador.id
  enabled  = true
  name     = "CMU LDAP"
  vendor   = "AD"

  # Connection and authentication settings
  connection_url     = "ldaps://ldap.cmu.edu"
  use_truststore_spi = "ALWAYS"
  connection_pooling = true
  bind_dn            = "uid=scottylabs-svc,ou=andrewperson,dc=andrew,dc=cmu,dc=edu"
  bind_credential    = var.cmu_ldap_bind_password

  # LDAP searching and updating
  edit_mode                 = "UNSYNCED"
  users_dn                  = "ou=andrewperson,dc=andrew,dc=cmu,dc=edu"
  username_ldap_attribute   = "uid"
  rdn_ldap_attribute        = "uid"
  uuid_ldap_attribute       = "guid"
  user_object_classes       = ["cmuAccountPerson,inetOrgPerson"]
  custom_user_search_filter = "(objectClass=cmuAccountPerson)"
  search_scope              = "ONE_LEVEL"

  # Synchronization settings
  import_enabled      = true
  batch_size_for_sync = 0

  # Advanced settings
  trust_email = true
}
