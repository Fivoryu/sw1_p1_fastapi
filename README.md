# Workflow AI Service

Servicio base en Python para preparar la capa de IA que transforma lenguaje natural en diagramas ejecutables.

## Objetivo inicial

Esta primera versión no entrena un modelo pesado. Deja listo el esqueleto para:
- construir datasets masivos a partir de ejemplos de negocio
- normalizar prompts de lenguaje natural
- generar una representación intermedia del workflow
- devolver BPMN/UML estructurado como salida futura

## Endpoints

- `GET /health`
- `POST /v1/diagram/generate`
- `POST /v1/datasets/build-examples`

## Arranque local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8090
```

## Estructura

- `app/main.py`: API FastAPI
- `app/schemas.py`: contratos de entrada/salida
- `app/services/diagram_generator.py`: servicio base para convertir prompt a estructura de workflow
- `app/services/dataset_builder.py`: utilidades para preparar ejemplos de entrenamiento a partir de datos masivos
- `data/training_examples.jsonl`: ejemplos seed para futura afinación o retrieval

## Integración esperada

Spring Boot consumirá este servicio vía REST para:
- `CU5` Generar Diagrama por Prompt
- OCR y enriquecimiento futuro
- simulación y análisis posterior
