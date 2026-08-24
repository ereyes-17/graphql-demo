# AWS EKS Helm Deployment Guide

This guide deploys the GraphQL API and PostgreSQL database to an AWS EKS cluster using the Helm charts in [k8s/helm/](k8s/helm/).

## Prerequisites

Install and configure the following tools on your workstation:

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [eksctl](https://eksctl.io/installation/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)

You also need an AWS account with permissions to create EKS clusters, VPCs, IAM roles, EC2 instances, and Elastic Load Balancers.

## 1. Configure AWS Credentials

Run `aws configure` and provide your AWS credentials. These are used by both the AWS CLI and `eksctl` to create resources in your account.

```bash
aws configure
```

You will be prompted for:

```
AWS Access Key ID [None]: AKIA...
AWS Secret Access Key [None]: ...
Default region name [None]: us-east-1
Default output format [None]: json
```

To verify the configuration, list the caller identity:

```bash
aws sts get-caller-identity
```

Expected output:

```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-user"
}
```

## 2. Create the EKS Cluster

Create a managed EKS cluster with two `t3.small` nodes in `us-east-1`:

```bash
eksctl create cluster --name my-cluster --region us-east-1 --node-type t3.small --nodes 2
```

This command:

- Creates a VPC, subnets, and security groups.
- Provisions the EKS control plane.
- Creates a managed node group with two worker nodes.
- Writes a `kubeconfig` entry so `kubectl` can talk to the cluster.

Wait for the cluster to finish provisioning. This usually takes 10–15 minutes.

## 3. Verify the Kubernetes Context

Confirm `kubectl` is pointing at the new EKS cluster:

```bash
kubectl config current-context
```

Expected output:

```
<your-aws-user>@my-cluster.us-east-1.eksctl.io
```

Verify the worker nodes are ready:

```bash
kubectl get nodes
```

Expected output:

```
NAME                                          STATUS   ROLES    AGE     VERSION
ip-192-168-XX-XX.us-east-1.compute.internal   Ready    <none>   2m      v1.XX.X-eks-XXXXXX
ip-192-168-YY-YY.us-east-1.compute.internal   Ready    <none>   2m      v1.XX.X-eks-XXXXXX
```

## 4. Enable IAM OIDC Provider

The EBS CSI driver needs an IAM role associated with a Kubernetes service account. First, associate an IAM OIDC provider with the cluster:

```bash
eksctl utils associate-iam-oidc-provider \
  --region=us-east-1 \
  --cluster=my-cluster \
  --approve
```

## 5. Create the EBS CSI Driver IAM Service Account

Create a service account in the `kube-system` namespace and attach the AWS managed EBS CSI driver policy:

```bash
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster my-cluster \
  --region us-east-1 \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve \
  --override-existing-serviceaccounts
```

## 6. Install the AWS EBS CSI Driver Add-on

Install the Amazon EBS CSI driver add-on so Kubernetes can dynamically provision EBS volumes for PersistentVolumeClaims:

```bash
aws eks create-addon \
  --cluster-name my-cluster \
  --addon-name aws-ebs-csi-driver \
  --region us-east-1 \
  --service-account-role-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/AmazonEKS_EBS_CSI_DriverRole
```

Wait for the add-on to become active:

```bash
aws eks wait addon-active \
  --cluster-name my-cluster \
  --addon-name aws-ebs-csi-driver \
  --region us-east-1
```

If the add-on was already running before the IAM service account was linked, restart the EBS CSI controller deployment so it picks up the new permissions:

```bash
kubectl rollout restart deployment ebs-csi-controller -n kube-system
```

## 7. Mark gp2 as the Default StorageClass

The PostgreSQL StatefulSet requests a PersistentVolumeClaim. Mark `gp2` as the default StorageClass so Kubernetes can provision EBS volumes automatically:

```bash
kubectl patch storageclass gp2 \
  -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

Verify the default StorageClass:

```bash
kubectl get storageclass
```

`gp2` should now show `(default)` next to its name.

## 8. Install the NGINX Ingress Controller

Add the official NGINX Ingress chart repository and install the controller. On AWS, the controller creates a LoadBalancer service that provisions an AWS Elastic Load Balancer.

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

Wait for the controller to be ready:

```bash
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s
```

Retrieve the external address of the load balancer:

```bash
kubectl get service ingress-nginx-controller -n ingress-nginx
```

Example output:

```
NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP                                                               PORT(S)
ingress-nginx-controller   LoadBalancer   10.100.123.45   a1b2c3d4e5f6g7h8-1234567890.us-east-1.elb.amazonaws.com   80:31234/TCP,443:31235/TCP
```

Copy the `EXTERNAL-IP` value. You will use it to access the API.

## 9. Create the Application Namespace

```bash
kubectl create namespace graphql-demo
```

## 10. Deploy PostgreSQL

Install the PostgreSQL Helm chart:

```bash
helm install postgres ./k8s/helm/postgres -n graphql-demo
```

Wait for Postgres to start before installing the API:

```bash
kubectl rollout status statefulset/postgres -n graphql-demo
```

## 11. Deploy the GraphQL API

The default chart values use `graphql-demo.local` as the Ingress host, which is only useful for local development. For AWS, the simplest approach is to remove the host requirement so the ELB hostname works directly.

Install the API chart:

```bash
helm install graphql-demo-api ./k8s/helm/api -n graphql-demo
```

Wait for the API to roll out:

```bash
kubectl rollout status deployment/graphql-demo-api -n graphql-demo
```

> **Note:** If you want to use a custom domain instead, see [AWS_EKS_ROUTE53_DNS.md](AWS_EKS_ROUTE53_DNS.md).

## 12. Access the API

### Option A: Load balancer hostname (default)

Use the `EXTERNAL-IP` from step 8:

```
http://abe59f1b075504e0f9f68c3835d26e9b-1931459861.us-east-1.elb.amazonaws.com/graphql/
```

### Option B: Custom domain

If you configured a Route 53 DNS record, browse to:

```
http://graphql-demo.api.com/graphql/
```

See [AWS_EKS_ROUTE53_DNS.md](AWS_EKS_ROUTE53_DNS.md) for the full setup.

### Option C: Port-forward for debugging

```bash
kubectl port-forward service/graphql-demo-api 8000:8000 -n graphql-demo
```

Then open:

```
http://localhost:8000/graphql/
```

## Upgrading a Release

After changing values or templates:

```bash
helm upgrade postgres ./k8s/helm/postgres -n graphql-demo
helm upgrade graphql-demo-api ./k8s/helm/api -n graphql-demo
```

## Uninstalling

Remove the application releases:

```bash
helm uninstall graphql-demo-api -n graphql-demo
helm uninstall postgres -n graphql-demo
helm uninstall ingress-nginx -n ingress-nginx
kubectl delete namespace graphql-demo
kubectl delete namespace ingress-nginx
```

Delete the EKS cluster and all associated AWS resources:

```bash
eksctl delete cluster --name my-cluster --region us-east-1
```

> **Warning:** `eksctl delete cluster` removes the VPC, subnets, load balancers, and node groups. This cannot be undone.

## Useful Commands

List Helm releases:

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

View Postgres logs:

```bash
kubectl logs -n graphql-demo -l app.kubernetes.io/instance=postgres --tail=100 -f
```

## Notes

- The API image in the chart defaults to `ereyes2017/graphql-demo:latest`. If you build and push your own image, override it with `--set workload.image=<your-image>`.
- AWS `t3.small` instances provide 2 vCPU and 2 GiB memory. If the API or Postgres pods are `Pending` due to insufficient resources, scale the node group or use a larger instance type.
- The first time a node pulls the `ereyes2017/graphql-demo:latest` image it may take a minute or two.
