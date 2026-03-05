# Labrador realm
resource "keycloak_realm" "labrador" {
  realm                       = "labrador"
  default_signature_algorithm = "RS256"
  remember_me                 = true
}

resource "keycloak_group" "admins" {
  realm_id = keycloak_realm.labrador.id
  name     = var.admin_group_name
}

resource "keycloak_group_memberships" "admins" {
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.admins.id
  members  = jsondecode(file("tf.json")).admins
}
