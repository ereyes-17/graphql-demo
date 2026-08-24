# AWS EKS Route 53 DNS Guide

This guide explains how to expose the GraphQL API on a custom domain using Amazon Route 53 and the NGINX Ingress Controller deployed in [AWS_EKS_HELM_DEPLOY.md](AWS_EKS_HELM_DEPLOY.md).

## Prerequisites

- A running EKS cluster with the NGINX Ingress Controller installed.
- The API Helm release installed with a custom `ingress.host` value.
- An AWS account with Route 53 permissions.

## 1. Grant Route 53 Permissions

Attach the managed Route 53 policy to your IAM user if it is not already attached:

```bash
aws iam attach-user-policy \
  --user-name reyesadmin \
  --policy-arn arn:aws:iam::aws:policy/AmazonRoute53FullAccess
```

## 2. Create a Route 53 Hosted Zone

Create a public hosted zone for your domain. Replace `api.com` with a domain you actually own.

```bash
aws route53 create-hosted-zone \
  --name api.com \
  --caller-reference $(date +%s)
```

Note the hosted zone ID from the output.

## 3. Update Domain Registrar Nameservers

For the hosted zone to resolve on the public internet, the domain's registrar must delegate DNS to the Route 53 nameservers for the zone. Retrieve the nameservers:

```bash
aws route53 get-hosted-zone --id <HOSTED_ZONE_ID>
```

Update your registrar's nameserver records to match the `NameServers` returned by AWS.

## 4. Install the API Chart with a Custom Host

Create a custom values file, for example `values-aws.yaml`:

```yaml
ingress:
  host: graphql-demo.api.com
```

Install or upgrade the API chart with the override:

```bash
helm install graphql-demo-api ./k8s/helm/api -n graphql-demo -f values-aws.yaml
```

If the chart is already installed, upgrade it:

```bash
helm upgrade graphql-demo-api ./k8s/helm/api -n graphql-demo -f values-aws.yaml
```

## 5. Get the Ingress Load Balancer Hostname

```bash
kubectl get service ingress-nginx-controller -n ingress-nginx
```

Copy the value from the `EXTERNAL-IP` column, for example:

```
abe59f1b075504e0f9f68c3835d26e9b-1931459861.us-east-1.elb.amazonaws.com
```

## 6. Create the Route 53 Record

Create a CNAME record that points your custom hostname to the load balancer. Replace `<HOSTED_ZONE_ID>` with your zone ID.

```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id <HOSTED_ZONE_ID> \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "graphql-demo.api.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{
          "Value": "abe59f1b075504e0f9f68c3835d26e9b-1931459861.us-east-1.elb.amazonaws.com"
        }]
      }
    }]
  }'
```

## 7. Verify DNS Resolution

Wait a few minutes for propagation, then verify the record resolves:

```bash
nslookup graphql-demo.api.com
```

or

```bash
dig graphql-demo.api.com
```

## 8. Access the API

Browse to:

```
http://graphql-demo.api.com/graphql/
```

Or test with curl:

```bash
curl http://graphql-demo.api.com/graphql/
```

## Troubleshooting

- If `nslookup` fails, confirm the registrar is using the Route 53 nameservers and the CNAME value matches the ELB hostname exactly.
- If DNS resolves but you get a 404, verify the Ingress host matches the URL you are using:

```bash
kubectl describe ingress graphql-demo-api -n graphql-demo
```
