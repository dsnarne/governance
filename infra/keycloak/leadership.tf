# Populate the leadership group with members and admins from the admins.json file.

resource "keycloak_group" "leadership" {
  realm_id = keycloak_realm.labrador.id
  name     = var.leadership_group_name
}

resource "keycloak_group_memberships" "leadership_members" {
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.leadership.id
  members  = jsondecode(file("admins.json")).leadership.members
}

resource "keycloak_group" "leadership_admins" {
  realm_id  = keycloak_realm.labrador.id
  name      = "${var.leadership_group_name}-${var.admin_group_suffix}"
  parent_id = keycloak_group.leadership.id
}

resource "keycloak_group_memberships" "leadership_admins" {
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.leadership_admins.id
  members  = jsondecode(file("admins.json")).leadership.admins
}

