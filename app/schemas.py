from pydantic import BaseModel, Field


class DiagramGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=5)
    business_context: str | None = None
    output_format: str = "bpmn"


class DiagramGenerationResponse(BaseModel):
    success: bool
    normalized_prompt: str
    detected_steps: list[dict]
    generated_structure: dict
    output_format: str


class DatasetBuildRequest(BaseModel):
    source_name: str
    examples: list[dict]


class DatasetBuildResponse(BaseModel):
    success: bool
    source_name: str
    examples_count: int
    sample: list[dict]
