# Local Kubernetes Dashboard

This guide explains how to deploy and access the Kubernetes Dashboard on a local cluster (for example, kind, minikube, or Docker Desktop Kubernetes).

## Prerequisites

- A running Kubernetes cluster.
- `kubectl` configured to communicate with the cluster.

## Deploy the Dashboard

Apply the official Kubernetes Dashboard manifest:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
```

## Create an Admin User

The dashboard requires authentication. Create a ServiceAccount with `cluster-admin` privileges:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
EOF
```

> ⚠️ In a real cluster, avoid granting `cluster-admin` to dashboard users. Create a Role or ClusterRole with only the permissions needed.

## Get the Login Token

Generate a bearer token for the admin user:

```bash
kubectl -n kubernetes-dashboard create token admin-user
```

Copy the entire token output. It is a long base64-encoded string printed across multiple lines.

## Start the Proxy

Run `kubectl proxy` to expose the dashboard locally:

```bash
kubectl proxy
```

The proxy serves on `http://127.0.0.1:8001`.

## Access the Dashboard

Open the following URL in your browser:

```
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

On the login screen:

1. Select **Token**.
2. Paste the token copied earlier.
3. Click **Sign in**.

## Stop the Proxy

In the terminal running `kubectl proxy`, press `Ctrl+C`.

## Recreate the Token Later

Tokens are temporary. Generate a new one anytime with:

```bash
kubectl -n kubernetes-dashboard create token admin-user
```

## Remove the Dashboard

To uninstall the dashboard and admin user:

```bash
kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl delete clusterrolebinding admin-user
kubectl delete serviceaccount admin-user -n kubernetes-dashboard
```
