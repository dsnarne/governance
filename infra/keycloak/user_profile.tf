locals {
  view_permissions = ["admin", "user"]
  edit_permissions = ["admin"]
}

resource "keycloak_realm_user_profile" "userprofile" {
  realm_id = keycloak_realm.labrador.id

  attribute {
    name         = keycloak_user_template_importer_identity_provider_mapper.username.name
    display_name = "$${username}"


    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = "email"
    display_name = "$${email}"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.full_email.user_model_attribute
    display_name = "Full Email"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.first_name.user_model_attribute
    display_name = "$${firstName}"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.last_name.user_model_attribute
    display_name = "$${lastName}"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.full_name.user_model_attribute
    display_name = "Full Name"


    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.display_name.user_model_attribute
    display_name = "Display Name"


    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  # --- CMU Extended Metadata ---
  attribute {
    name         = keycloak_ldap_user_attribute_mapper.affiliations.user_model_attribute
    display_name = "Affiliations"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.departments.user_model_attribute
    display_name = "Departments"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.colleges.user_model_attribute
    display_name = "Colleges"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.class.user_model_attribute
    display_name = "Class"


    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  group {
    name                = "user-metadata"
    display_header      = "User metadata"
    display_description = "Attributes, which refer to user metadata"
  }
}
