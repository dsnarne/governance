terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "5.7.0"
    }
  }
}

provider "vault" {
  address = var.secrets_url
  token   = var.vault_token
}
