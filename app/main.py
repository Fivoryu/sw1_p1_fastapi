from fastapi import FastAPI
from fastapi import Request

from app.schemas import (
    DatasetBuildRequest,
    DatasetBuildResponse,
    DiagramGenerationRequest,
    DiagramGenerationResponse,
)
from app.services.dataset_builder import DatasetBuilderService
from app.services.diagram_generator import DiagramGeneratorService
from app.db import mongo

app = FastAPI(title="Workflow AI Service", version="0.1.0")

diagram_generator = DiagramGeneratorService()
dataset_builder = DatasetBuilderService()


@app.on_event("startup")
async def startup_event():
    await mongo.connect(app)


@app.on_event("shutdown")
def shutdown_event():
    mongo.close()


@app.get("/health")
async def health(request: Request) -> dict:
    status = {"service": "workflow-ai-service", "status": "ok"}
    # include a quick DB ping if available
    try:
        client = getattr(request.app.state, "mongo_client", None)
        mongo_error = getattr(request.app.state, "mongo_error", None)
        if client is not None:
            await client.admin.command("ping")
            status["mongo"] = "connected"
        elif mongo_error:
            status["mongo"] = f"error: {mongo_error}"
        else:
            status["mongo"] = "not-configured"
    except Exception as e:
        status["mongo"] = f"error: {e}"
    return status


@app.post("/v1/diagram/generate", response_model=DiagramGenerationResponse)
def generate_diagram(payload: DiagramGenerationRequest) -> DiagramGenerationResponse:
    normalized_prompt = diagram_generator.normalize_prompt(payload.prompt)
    steps = diagram_generator.detect_steps(normalized_prompt)
    if payload.output_format == "uml_activity":
        structure = diagram_generator.generate_uml_activity_structure(normalized_prompt, payload.business_context)
    else:
        structure = diagram_generator.generate_intermediate_structure(normalized_prompt)

    return DiagramGenerationResponse(
        success=True,
        normalized_prompt=normalized_prompt,
        detected_steps=steps,
        generated_structure=structure,
        output_format=payload.output_format,
    )


@app.post("/v1/datasets/build-examples", response_model=DatasetBuildResponse)
def build_examples(payload: DatasetBuildRequest) -> DatasetBuildResponse:
    dataset = dataset_builder.build_examples(payload.source_name, payload.examples)
    return DatasetBuildResponse(
        success=True,
        source_name=dataset["source_name"],
        examples_count=dataset["examples_count"],
        sample=dataset["examples"][:3],
    )
