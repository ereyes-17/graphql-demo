# Kubernetes Deployment Guide

This guide explains how to deploy the GraphQL API and its PostgreSQL database to a local Kubernetes cluster, including the NGINX Ingress controller and WSL2 port-forwarding.

## Prerequisites

- A running Kubernetes cluster (kind, minikube, Docker Desktop, etc.).
- `kubectl` configured to talk to the cluster.
- The Docker image pushed to a registry accessible by the cluster (for example, `ereyes2017/graphql-demo:latest`).

## Manifest Layout

```
k8s/
├── configs/graphql-demo-configmap.yaml      # Non-sensitive config (DB_HOST, DB_PORT, DB_NAME)
├── secrets/graphsql-demo-secret.yaml        # Sensitive config (DB_USER, DB_PASSWORD)
├── statefulsets/postgres-statefulset.yaml   # PostgreSQL database
├── services/postgres-service.yaml           # Postgres headless/cluster service
├── services/graphql-demo-service.yaml       # API cluster service
├── deployments/graphql-demo-deployment.yaml # API pods
└── ingress/graphql-demo-ingress.yaml        # Ingress rule
```

## 1. Create the Namespace

All manifests use the `graphql-demo` namespace:

```bash
kubectl create namespace graphql-demo
```

## 2. Install the NGINX Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

Wait for the controller to be ready:

```bash
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

## 3. Apply the Application Manifests

Apply in this order so ConfigMaps/Secrets exist before the workloads that consume them:

```bash
kubectl apply -f k8s/configs/
kubectl apply -f k8s/secrets/
kubectl apply -f k8s/statefulsets/
kubectl apply -f k8s/services/
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/ingress/
```

Wait for Postgres to be ready before expecting the API to start:

```bash
kubectl rollout status statefulset/postgres -n graphql-demo
kubectl rollout status deployment/graphql-demo-api -n graphql-demo
```

## 4. Access the API from WSL2

The simplest way to reach the API from WSL2 (and from the Windows host) is to port-forward the service:

```bash
kubectl port-forward service/graphql-demo-api 8000:8000 -n graphql-demo
```

Then open:

```
http://localhost:8000/graphql/
```

To stop the port-forward, press `Ctrl+C` in the terminal where it is running.

## 5. Optional: Access via Ingress

The Ingress rule matches the hostname `graphql-demo.local` and routes paths under `/` to the `graphql-demo-api` service on port `8000`.

### Why the simple `localhost:8080` URL does not work

The Ingress controller uses the `Host` header to pick a backend. If you port-forward the controller and browse to `http://localhost:8080/graphql/`, the request has `Host: localhost:8080`, which does **not** match `graphql-demo.local`, so you get a 404.

### Test with curl (no hosts file changes needed)

Port-forward the ingress controller:

```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80
```

Then send the correct `Host` header:

```bash
curl -H "Host: graphql-demo.local" http://localhost:8080/graphql/
```

### Test with a browser

1. Add the host to your hosts file.
   - On Windows (for WSL2): open `C:\Windows\System32\Drivers\etc\hosts` as Administrator and add:

     ```
     127.0.0.1 graphql-demo.local
     ```

2. Port-forward the ingress controller:

   ```bash
   kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80
   ```

3. Open the exact URL with the hostname, **not** `localhost`:

   ```
   http://graphql-demo.local:8080/graphql/
   ```

### Make the Ingress match any hostname (simplest for local testing)

If you do not need a custom hostname, edit [k8s/ingress/graphql-demo-ingress.yaml](k8s/ingress/graphql-demo-ingress.yaml) and remove the `host:` line:

```yaml
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: graphql-demo-api
            port:
              number: 8000
```

Reapply it:

```bash
kubectl apply -f k8s/ingress/graphql-demo-ingress.yaml
```

Now `http://localhost:8080/graphql/` works directly through the port-forward.

## Useful Commands

View pods:

```bash
kubectl get pods -n graphql-demo
```

View API logs:

```bash
kubectl logs -n graphql-demo -l app.kubernetes.io/instance=graphql-demo-api --tail=100 -f
```

View Postgres logs:

```bash
kubectl logs -n graphql-demo -l app.kubernetes.io/instance=postgres --tail=100 -f
```

Describe the ingress:

```bash
kubectl describe ingress graphql-demo -n graphql-demo
```

## Cleanup

Remove everything from the cluster:

```bash
kubectl delete -f k8s/ingress/
kubectl delete -f k8s/deployments/
kubectl delete -f k8s/services/
kubectl delete -f k8s/statefulsets/
kubectl delete -f k8s/secrets/
kubectl delete -f k8s/configs/
kubectl delete namespace graphql-demo
```

To remove the ingress controller:

```bash
kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```
