terraform {
  backend "s3" {
    skip_credentials_validation = true
    use_path_style              = true
  }
}
