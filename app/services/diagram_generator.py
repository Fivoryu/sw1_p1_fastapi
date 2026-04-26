class DiagramGeneratorService:
    def normalize_prompt(self, prompt: str) -> str:
        return " ".join(prompt.strip().split())

    def detect_steps(self, prompt: str) -> list[dict]:
        sentences = [item.strip() for item in prompt.replace("\n", ". ").split(".") if item.strip()]
        steps: list[dict] = []
        for index, sentence in enumerate(sentences, start=1):
            steps.append(
                {
                    "id": f"step_{index}",
                    "text": sentence,
                    "type": self._infer_step_type(sentence),
                }
            )
        return steps

    def generate_intermediate_structure(self, prompt: str) -> dict:
        normalized_prompt = self.normalize_prompt(prompt)
        steps = self.detect_steps(normalized_prompt)

        nodes = [{"id": "start", "type": "START", "label": "Inicio"}]
        flows = []
        previous_node_id = "start"

        for step in steps:
            node_id = step["id"]
            nodes.append(
                {
                    "id": node_id,
                    "type": step["type"],
                    "label": step["text"],
                }
            )
            flows.append({"source": previous_node_id, "target": node_id})
            previous_node_id = node_id

        nodes.append({"id": "end", "type": "END", "label": "Fin"})
        flows.append({"source": previous_node_id, "target": "end"})

        return {
            "nodes": nodes,
            "flows": flows,
            "metadata": {
                "strategy": "rule_based_bootstrap",
                "ready_for_training": True,
            },
        }

    def _infer_step_type(self, sentence: str) -> str:
        lowered = sentence.lower()
        if "si" in lowered or "else" in lowered or "sino" in lowered:
            return "DECISION"
        if "paralelo" in lowered or "simult" in lowered:
            return "PARALLEL"
        return "TASK"
