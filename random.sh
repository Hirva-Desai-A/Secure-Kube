cd ~/securekube/terraform

terraform init
terraform plan
terraform apply -auto-approve

# Verify namespaces created
kubectl get namespaces | grep securekube