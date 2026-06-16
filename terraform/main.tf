terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "kind-securekube"
}

resource "kubernetes_namespace" "securekube_monitoring" {
  metadata {
    name = "securekube-monitoring"
    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
      "project"                      = "securekube"
    }
  }
}

resource "kubernetes_namespace" "securekube_security" {
  metadata {
    name = "securekube-security"
    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
      "project"                      = "securekube"
    }
  }
}
