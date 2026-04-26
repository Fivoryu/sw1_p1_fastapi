from collections import Counter


class DatasetBuilderService:
    def build_examples(self, source_name: str, examples: list[dict]) -> dict:
        normalized = [self._normalize_example(example, index) for index, example in enumerate(examples, start=1)]
        step_types = Counter(step.get("type", "TASK") for example in normalized for step in example.get("steps", []))

        return {
            "source_name": source_name,
            "examples_count": len(normalized),
            "step_type_distribution": dict(step_types),
            "examples": normalized,
        }

    def _normalize_example(self, example: dict, index: int) -> dict:
        return {
            "id": example.get("id") or f"example_{index}",
            "prompt": (example.get("prompt") or "").strip(),
            "steps": example.get("steps") or [],
            "target_format": example.get("target_format") or "bpmn",
        }
