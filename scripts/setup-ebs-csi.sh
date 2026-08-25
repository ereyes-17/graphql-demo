#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
CLUSTER_NAME="${CLUSTER_NAME:-my-cluster}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/AmazonEKS_EBS_CSI_DriverRole"

echo "==> Associating IAM OIDC provider..."
eksctl utils associate-iam-oidc-provider \
  --region="${AWS_REGION}" \
  --cluster="${CLUSTER_NAME}" \
  --approve

echo "==> Cleaning up existing ebs-csi-controller-sa if present..."
kubectl delete serviceaccount ebs-csi-controller-sa -n kube-system --ignore-not-found

echo "==> Creating IAM service account for EBS CSI driver..."
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster "${CLUSTER_NAME}" \
  --region "${AWS_REGION}" \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve

echo "==> Checking for existing failed EBS CSI add-on..."
ADDON_STATUS=$(aws eks describe-addon \
  --cluster-name "${CLUSTER_NAME}" \
  --addon-name aws-ebs-csi-driver \
  --region "${AWS_REGION}" \
  --query 'addon.status' \
  --output text 2>/dev/null || echo "NOT_FOUND")

if [[ "${ADDON_STATUS}" == "CREATE_FAILED" || "${ADDON_STATUS}" == "DEGRADED" || "${ADDON_STATUS}" == "ACTIVE" ]]; then
  echo "==> Deleting existing add-on (status: ${ADDON_STATUS})..."
  aws eks delete-addon \
    --cluster-name "${CLUSTER_NAME}" \
    --addon-name aws-ebs-csi-driver \
    --region "${AWS_REGION}"

  echo "==> Waiting for add-on deletion..."
  aws eks wait addon-deleted \
    --cluster-name "${CLUSTER_NAME}" \
    --addon-name aws-ebs-csi-driver \
    --region "${AWS_REGION}"
fi

echo "==> Installing EBS CSI driver add-on..."
aws eks create-addon \
  --cluster-name "${CLUSTER_NAME}" \
  --addon-name aws-ebs-csi-driver \
  --region "${AWS_REGION}" \
  --service-account-role-arn "${ROLE_ARN}"

echo "==> Waiting for add-on to become active..."
aws eks wait addon-active \
  --cluster-name "${CLUSTER_NAME}" \
  --addon-name aws-ebs-csi-driver \
  --region "${AWS_REGION}"

echo "==> Marking gp2 as default StorageClass..."
kubectl patch storageclass gp2 \
  -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

echo "==> Restarting EBS CSI controller to pick up IAM role..."
kubectl rollout restart deployment ebs-csi-controller -n kube-system

echo "==> EBS CSI driver setup complete."
