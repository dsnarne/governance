# Parent group for all teams
resource "keycloak_group" "teams" {
  realm_id = keycloak_realm.labrador.id
  name     = "teams"
}

# Team groups
locals {
  team_slugs = toset(keys(var.teams_data))
}

resource "keycloak_group" "team_groups" {
  for_each  = local.team_slugs
  realm_id  = keycloak_realm.labrador.id
  parent_id = keycloak_group.teams.id
  name      = each.key
}

resource "keycloak_group" "team_admins_groups" {
  for_each  = local.team_slugs
  realm_id  = keycloak_realm.labrador.id
  parent_id = keycloak_group.team_groups[each.key].id
  name      = "${each.key}-${var.admin_group_suffix}"
}

# Team memberships
resource "keycloak_group_memberships" "team_memberships" {
  for_each = local.team_slugs
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.team_groups[each.key].id
  members  = var.teams_data[each.key].members
}

resource "keycloak_group_memberships" "team_admins_memberships" {
  for_each = local.team_slugs
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.team_admins_groups[each.key].id
  members  = var.teams_data[each.key].admins
}
