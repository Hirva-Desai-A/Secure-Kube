#!/bin/bash
set -e

# Automatically navigate to the directory where this script is located
cd "$(dirname "$0")"

echo "🚀 Starting SecureKube Complete Setup..."

# 1. Provision Cluster
echo "📦 Creating Kubernetes cluster using Kind..."
kind create cluster --config k8s/kind-config.yaml --name securekube || echo "Cluster may already exist. Proceeding..."

# 2. Build Docker Images
echo "🐳 Building Docker images locally..."
# Adding --load ensures the image is forced into the local docker daemon
docker build --load -t securekube-app:latest ./app
docker build --load -t securekube-app2:latest ./app2
docker build --load -t securekube-remediation:latest ./remediation

# 3. Load Images into Kind Cluster (Using tarball method for WSL compatibility)
echo "🚚 Exporting and loading images into Kind cluster..."
# Save to tar archives
docker save securekube-app:latest -o app.tar
docker save securekube-app2:latest -o app2.tar
docker save securekube-remediation:latest -o remediation.tar

# Load archives into kind
kind load image-archive app.tar --name securekube
kind load image-archive app2.tar --name securekube
kind load image-archive remediation.tar --name securekube

# Clean up tar files
rm app.tar app2.tar remediation.tar

# 4. Apply Namespaces
echo "🏗️ Applying namespaces..."
kubectl apply -f k8s/manifests/namespace.yaml

# 5. Deploy Database (Postgres)
echo "🗄️ Deploying PostgreSQL..."
kubectl apply -f k8s/database/

# 6. Apply Zero-Trust and Self-Healing Controls
echo "🔐 Applying zero-trust and self-healing policies..."
kubectl apply -f k8s/manifests/network-policies.yaml
kubectl apply -f k8s/manifests/self-healing-policy.yaml

# 7. Setup Monitoring (Prometheus & Loki)
echo "📊 Setting up Monitoring Stack..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  -f k8s/monitoring/prometheus-values.yaml \
  -n monitoring --create-namespace

helm install loki grafana/loki-stack \
  -f k8s/monitoring/loki-values.yaml \
  -n monitoring

kubectl apply -f k8s/monitoring/servicemonitors.yaml
kubectl apply -f k8s/monitoring/extreme-memory-patch.yaml

# 8. Setup Security (Falco & Falcosidekick)
echo "🛡️ Setting up Falco Runtime Security..."
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

helm install falco falcosecurity/falco \
  -f falco/falco-values.yaml \
  -f falco/custom-rules.yaml \
  -f falco/falco-micro-resources.yaml \
  -n falco --create-namespace

helm install falcosidekick falcosecurity/falcosidekick \
  -f falco/falcosidekick-values.yaml \
  -n falco

# 9. Service Mesh & Zero-Trust (Istio)
echo "🔐 Applying Istio & mTLS Zero-Trust policies..."
kubectl apply -f k8s/manifests/istio-zero-trust.yaml
kubectl apply -f k8s/manifests/mtls-policy.yaml
kubectl apply -f k8s/manifests/zero-trust-policy.yaml

# 10. Deploy Applications
echo "🚀 Deploying Microservices & Remediation..."
kubectl apply -f k8s/manifests/deployment.yaml
kubectl apply -f k8s/manifests/payment-deployment.yaml
kubectl apply -f k8s/manifests/service.yaml
kubectl apply -f k8s/manifests/remediation.yaml

echo "✅ SecureKube Setup Complete!"