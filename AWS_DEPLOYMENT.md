# AWS deployment

Este repositorio queda listo para desplegarse en AWS App Runner usando contenedores publicados en Amazon ECR.

## Recursos AWS necesarios

- Un repositorio de Amazon ECR
- Un servicio de AWS App Runner apuntando a ese repositorio
- Un rol IAM para GitHub Actions con acceso a ECR y App Runner

## Variables de GitHub Actions

Configura estas `Repository variables`:

- `AWS_REGION`
- `ECR_REPOSITORY`
- `APP_RUNNER_SERVICE_ARN`

Configura este `Repository secret`:

- `AWS_ROLE_ARN`

## Variables de entorno del servicio App Runner

- `MONGO_URI` opcional si el servicio necesita conectarse a MongoDB
- `MONGO_DB` opcional, por defecto `workflow1`
- `PORT` opcional, por defecto `8080`

## Flujo de despliegue

- Cada push a `main` ejecuta `.github/workflows/aws-deploy.yml`
- El workflow valida la app, construye la imagen y la publica en ECR
- Después solicita un nuevo despliegue del servicio App Runner
