# Local Jenkins with Docker Compose

This setup runs Jenkins locally in a Docker container with the tools needed to build, test, and deploy the GraphQL API to AWS EKS.

## Files

- [docker-compose.yml](docker-compose.yml) — Jenkins service definition
- [Dockerfile](Dockerfile) — Custom Jenkins image with Docker, kubectl, Helm, and eksctl
- [plugins.txt](plugins.txt) — Jenkins plugins for SCM, Pipeline, GitHub, and AWS/EKS

## Start Jenkins

```bash
cd docker/jenkins
docker compose up -d --build
```

The first build will take a few minutes because it installs the plugins and CLI tools.

## Access Jenkins

Open:

```
http://localhost:8080
```

The setup wizard is disabled. You can log in as the default admin user or configure security under **Manage Jenkins → Security**.

## Get the initial admin password

If you need the initial password:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

## Configure the Pipeline

1. Go to **New Item → Multibranch Pipeline**.
2. Add your Git repository under **Branch Sources**.
3. Set **Build Configuration → Mode** to `by Jenkinsfile`.
4. Add a trigger:
   - **GitHub hook trigger for GITScm polling** for webhook-based builds, or
   - **Scan Multibranch Pipeline Triggers → Periodically every X minutes**.

The repository's [Jenkinsfile](../../Jenkinsfile) builds the Docker image, pushes it to ECR, and deploys to EKS.

## Required Jenkins Credentials

- **AWS Credentials** with ID `aws-credentials` — used to access ECR and EKS.
- **Git credentials** — used to pull the repository.

## Useful Commands

View logs:

```bash
docker logs -f jenkins
```

Restart Jenkins:

```bash
docker compose restart
```

Stop and remove Jenkins:

```bash
docker compose down
```

To remove the persistent Jenkins data volume:

```bash
docker compose down -v
```
