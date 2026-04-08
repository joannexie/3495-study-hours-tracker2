# Project 2 AWS + Kubernetes Guide for Study Hours Tracker

This package contains starter Kubernetes manifests and helper commands for deploying the Study Hours Tracker microservices to Amazon EKS.

Files:
- `k8s/00-namespace.yaml`
- `k8s/01-secret.yaml`
- `k8s/02-mysql.yaml`
- `k8s/03-mongo.yaml`
- `k8s/04-auth.yaml`
- `k8s/05-enter.yaml`
- `k8s/06-analytics.yaml`
- `k8s/07-show.yaml`
- `k8s/08-hpa.yaml`
- `cluster-autoscaler-values.yaml`
- `build-and-push.sh`

Use these as a starting point and update the ECR image URLs before deploying.
