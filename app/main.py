from fastapi import FastAPI

from app.schemas import (
    DatasetBuildRequest,
    DatasetBuildResponse,
    DiagramGenerationRequest,
    DiagramGenerationResponse,
)
from app.services.dataset_builder import DatasetBuilderService
from app.services.diagram_generator import DiagramGeneratorService

app = FastAPI(title="Workflow AI Service", version="0.1.0")

diagram_generator = DiagramGeneratorService()
dataset_builder = DatasetBuilderService()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "workflow-ai-service"}


@app.post("/v1/diagram/generate", response_model=DiagramGenerationResponse)
def generate_diagram(payload: DiagramGenerationRequest) -> DiagramGenerationResponse:
    normalized_prompt = diagram_generator.normalize_prompt(payload.prompt)
    steps = diagram_generator.detect_steps(normalized_prompt)
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
