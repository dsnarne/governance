terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "5.7.0"
    }
  }
}

provider "vault" {
  address = "https://bao.scottylabs.org"
  token   = var.vault_token
}
