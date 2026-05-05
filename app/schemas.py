from pydantic import BaseModel, Field
from typing import Literal


class DiagramGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=5)
    business_context: str | None = None
    output_format: Literal["bpmn", "uml_activity"] = "uml_activity"


class DiagramGenerationResponse(BaseModel):
    success: bool
    normalized_prompt: str
    detected_steps: list[dict]
    generated_structure: dict
    output_format: str
    bpmn_xml: str | None = None
    warnings: list[str] = []


class DatasetBuildRequest(BaseModel):
    source_name: str
    examples: list[dict]


class DatasetBuildResponse(BaseModel):
    success: bool
    source_name: str
    examples_count: int
    sample: list[dict]
