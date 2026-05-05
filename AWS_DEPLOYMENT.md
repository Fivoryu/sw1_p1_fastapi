# AWS deployment

Este repositorio incluye un `Dockerfile` y un workflow que publica la imagen en Amazon ECR y fuerza un nuevo despliegue en **Amazon ECS** (Fargate u otro compatible con `update-service`).

## Recursos AWS necesarios

- Un repositorio de Amazon ECR
- Un cluster y servicio ECS que ejecuten esta imagen
- Un rol IAM para GitHub Actions con acceso a ECR y ECS

## Variables de GitHub Actions

Configura estas `Repository variables`:

- `AWS_REGION`
- `ECR_REPOSITORY`
- `ECS_CLUSTER`
- `ECS_SERVICE`

Configura este `Repository secret`:

- `AWS_ROLE_ARN`

## Variables de entorno del contenedor (ECS / tarea)

- `MONGO_URI` opcional si el servicio necesita conectarse a MongoDB
- `MONGO_DB` opcional, por defecto `workflow1`
- `PORT` opcional, por defecto `8080`

## Flujo de despliegue

- Cada push a `main` ejecuta `.github/workflows/aws-deploy.yml`
- El workflow construye la imagen Docker y la publica en ECR
- Después ejecuta `aws ecs update-service --force-new-deployment` sobre el servicio configurado
