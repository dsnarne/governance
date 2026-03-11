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
    name         = keycloak_ldap_user_attribute_mapper.middle_name.user_model_attribute
    display_name = "Middle Name"

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

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.orcid.user_model_attribute
    display_name = "ORCID"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.primary_affiliation.user_model_attribute
    display_name = "Primary Affiliation"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.affiliations.user_model_attribute
    display_name = "Affiliations"
    multi_valued = true

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.departments.user_model_attribute
    display_name = "Departments"
    multi_valued = true

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.colleges.user_model_attribute
    display_name = "Colleges"
    multi_valued = true

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.level.user_model_attribute
    display_name = "Level"

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

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.status.user_model_attribute
    display_name = "Status"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.creation_date.user_model_attribute
    display_name = "Creation Date"

    permissions {
      view = local.view_permissions
      edit = local.edit_permissions
    }
  }

  attribute {
    name         = keycloak_ldap_user_attribute_mapper.modify_date.user_model_attribute
    display_name = "Modify Date"

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
