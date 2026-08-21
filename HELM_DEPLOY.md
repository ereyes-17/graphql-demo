# Helm Deployment Guide

This guide explains how to deploy the GraphQL API and PostgreSQL database using the Helm charts in [k8s/helm/](k8s/helm/).

## Chart Layout

```
k8s/helm/
├── api/              # GraphQL API Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── postgres/         # PostgreSQL Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
└── ingress-nginx/    # Ingress controller values (optional)
```

## 1. Install the NGINX Ingress Controller with Helm

Add the official chart repository and install the controller:

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

Wait for it to be ready:

```bash
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

## 2. Create the Application Namespace

```bash
kubectl create namespace graphql-demo
```

## 3. Deploy PostgreSQL

```bash
helm install postgres ./k8s/helm/postgres -n graphql-demo
```

Wait for Postgres to start before installing the API:

```bash
kubectl rollout status statefulset/postgres -n graphql-demo
```

## 4. Deploy the GraphQL API

```bash
helm install graphql-demo-api ./k8s/helm/api -n graphql-demo
```

Wait for the API to roll out:

```bash
kubectl rollout status deployment/graphql-demo-api -n graphql-demo
```

## 5. Access the API

### Option A: Port-forward the service (simplest for WSL2)

```bash
kubectl port-forward service/graphql-demo-api 8000:8000 -n graphql-demo
```

Open:

```
http://localhost:8000/graphql/
```

This URL works from both WSL2 and the Windows host because WSL2 `localhost` is shared.

### Option B: Access through the Ingress controller

The API chart includes an Ingress resource using the hostname `graphql-demo.local`. Forward the ingress controller service:

```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80
```

From WSL2, send the correct `Host` header:

```bash
curl -H "Host: graphql-demo.local" http://localhost:8080/graphql/
```

From Windows, add this line to `C:\Windows\System32\Drivers\etc\hosts` as Administrator:

```
127.0.0.1 graphql-demo.local
```

Then browse to:

```
http://graphql-demo.local:8080/graphql/
```

> Windows can reach `localhost:8080` because the port-forward runs in WSL2 and WSL2 shares `localhost` with the host.

## Upgrading a Release

After changing values or templates:

```bash
helm upgrade postgres ./k8s/helm/postgres -n graphql-demo
helm upgrade graphql-demo-api ./k8s/helm/api -n graphql-demo
```

## Customizing Values

Override values at install or upgrade time:

```bash
helm install graphql-demo-api ./k8s/helm/api \
  -n graphql-demo \
  --set workload.image=ereyes2017/graphql-demo:0.0.1 \
  --set microservice.replicas=3
```

Or create a custom values file, for example `values-staging.yaml`, and use it:

```bash
helm install graphql-demo-api ./k8s/helm/api \
  -n graphql-demo \
  -f values-staging.yaml
```

## Uninstalling

```bash
helm uninstall graphql-demo-api -n graphql-demo
helm uninstall postgres -n graphql-demo
helm uninstall ingress-nginx -n ingress-nginx
```

## Useful Commands

List releases:

```bash
helm list -n graphql-demo
```

Render templates without installing:

```bash
helm template graphql-demo-api ./k8s/helm/api -n graphql-demo
```

Get release values:

```bash
helm get values graphql-demo-api -n graphql-demo
```

View API logs:

```bash
kubectl logs -n graphql-demo -l app.kubernetes.io/instance=graphql-demo-api --tail=100 -f
```
