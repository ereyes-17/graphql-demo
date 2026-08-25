# Jenkins Deployment Guide

This guide deploys Jenkins to the EKS cluster using the manifests in [k8s/jenkins/artifacts/](k8s/jenkins/artifacts/).

## Prerequisites

- A running EKS cluster.
- The AWS EBS CSI driver installed and `gp2` set as the default StorageClass.
- The NGINX Ingress Controller installed.
- `kubectl` configured to talk to the cluster.

## Deploy Jenkins

Apply the manifests in order:

```bash
kubectl apply -f k8s/jenkins/artifacts/namespace.yaml
kubectl apply -f k8s/jenkins/artifacts/serviceaccount.yaml
kubectl apply -f k8s/jenkins/artifacts/pvc.yaml
kubectl apply -f k8s/jenkins/artifacts/deployment.yaml
kubectl apply -f k8s/jenkins/artifacts/service.yaml
kubectl apply -f k8s/jenkins/artifacts/ingress.yaml
```

Wait for Jenkins to be ready:

```bash
kubectl rollout status deployment/jenkins -n jenkins
```

## Access Jenkins

Get the Ingress controller external address:

```bash
kubectl get service ingress-nginx-controller -n ingress-nginx
```

Browse to:

```
http://<EXTERNAL-IP>/
```

The Jenkins deployment in this guide disables the setup wizard. You can configure authentication and plugins after the first login.

## Get the Initial Admin Password

If the setup wizard is enabled, retrieve the initial password with:

```bash
kubectl exec -n jenkins deployment/jenkins -- cat /var/jenkins_home/secrets/initialAdminPassword
```

## Useful Commands

View Jenkins logs:

```bash
kubectl logs -n jenkins -l app=jenkins --tail=100 -f
```

Port-forward Jenkins locally:

```bash
kubectl port-forward -n jenkins service/jenkins 8080:8080
```

Then open:

```
http://localhost:8080
```

## Cleanup

```bash
kubectl delete -f k8s/jenkins/artifacts/
```
