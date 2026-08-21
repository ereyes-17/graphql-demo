# Docker Build & Deployment Guide

This guide covers how to build, push, and run the GraphQL API container, both locally and with Docker Compose.

## Build the Docker Image

From the project root (where the [Dockerfile](Dockerfile) is located):

```bash
docker build -t ereyes2017/graphql-demo:0.0.1 .
```

To tag the image as `latest` as well:

```bash
docker tag ereyes2017/graphql-demo:0.0.1 ereyes2017/graphql-demo:latest
```

## Push the Image to Docker Hub

```bash
docker push ereyes2017/graphql-demo:0.0.1
```

## Run the Container Standalone

```bash
docker run -d \
  --name my-graphql-app \
  -p 8000:8000 \
  -e DB_HOST=your-db-host \
  ereyes2017/graphql-demo:0.0.1
```

Replace `your-db-host` with the hostname or IP address of the PostgreSQL server the application should connect to.

## Run with Docker Compose

The included [docker-compose.yml](docker-compose.yml) starts both the PostgreSQL database and the GraphQL API service together.

Start the services in detached mode:

```bash
docker compose up -d
```

Stop and remove the services:

```bash
docker compose down
```

### Compose service layout

- `postgres` — PostgreSQL 16 database, accessible on host port `5432`.
- `my-graphql-app` — FastAPI/GraphQL API, accessible on host port `8000`.

The API container is configured with `DB_HOST: graphql_postgres` so it connects automatically to the Compose-managed database service.

## Useful Commands

View running logs:

```bash
docker logs -f my-graphql-app
```

List running containers:

```bash
docker ps
```

List all containers (including stopped):

```bash
docker ps -a
```
