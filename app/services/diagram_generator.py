import re


class DiagramGeneratorService:
    UML_VERSION = "2.5"

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
                    "partition": self._infer_partition(sentence),
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
                    "partition": step["partition"],
                }
            )
            flows.append({"id": f"flow_{len(flows) + 1}", "source": previous_node_id, "target": node_id})
            previous_node_id = node_id

        nodes.append({"id": "end", "type": "END", "label": "Fin"})
        flows.append({"id": f"flow_{len(flows) + 1}", "source": previous_node_id, "target": "end"})

        return {
            "nodes": nodes,
            "flows": flows,
            "metadata": {
                "strategy": "rule_based_bootstrap",
                "ready_for_training": True,
            },
        }

    def generate_uml_activity_structure(self, prompt: str, business_context: str | None = None) -> dict:
        normalized_prompt = self.normalize_prompt(prompt)
        steps = self.detect_steps(normalized_prompt)
        partitions = self._build_partitions(steps, business_context)
        fallback_partition_id = partitions[0]["id"]

        nodes = [
            {
                "id": "initial",
                "type": "INITIAL",
                "umlElement": "InitialNode",
                "label": "Inicio",
                "partition": fallback_partition_id,
            }
        ]
        edges = []
        previous_node_id = "initial"

        for index, step in enumerate(steps, start=1):
            node_type = self._to_uml_node_type(step["type"], step["text"])
            node_id = f"uml_{index}"
            nodes.append(
                {
                    "id": node_id,
                    "type": node_type,
                    "umlElement": self._uml_element_name(node_type),
                    "label": step["text"],
                    "partition": self._partition_id(step["partition"]),
                }
            )
            edges.append(self._edge(previous_node_id, node_id, len(edges) + 1))
            previous_node_id = node_id

            if node_type == "DECISION":
                action_id = f"uml_{index}_yes_action"
                merge_id = f"uml_{index}_merge"
                nodes.append(
                    {
                        "id": action_id,
                        "type": "ACTION",
                        "umlElement": "Action",
                        "label": "Ejecutar camino afirmativo",
                        "partition": self._partition_id(step["partition"]),
                    }
                )
                nodes.append(
                    {
                        "id": merge_id,
                        "type": "MERGE",
                        "umlElement": "MergeNode",
                        "label": "Unir resultado",
                        "partition": self._partition_id(step["partition"]),
                    }
                )
                edges.append(self._edge(node_id, action_id, len(edges) + 1, "[si]"))
                edges.append(self._edge(action_id, merge_id, len(edges) + 1))
                edges.append(self._edge(node_id, merge_id, len(edges) + 1, "[no]"))
                previous_node_id = merge_id

            if node_type == "FORK":
                parallel_action_id = f"uml_{index}_parallel_action"
                join_id = f"uml_{index}_join"
                nodes.append(
                    {
                        "id": parallel_action_id,
                        "type": "ACTION",
                        "umlElement": "Action",
                        "label": "Ejecutar ramas paralelas",
                        "partition": self._partition_id(step["partition"]),
                    }
                )
                nodes.append(
                    {
                        "id": join_id,
                        "type": "JOIN",
                        "umlElement": "JoinNode",
                        "label": "Sincronizar ramas",
                        "partition": self._partition_id(step["partition"]),
                    }
                )
                edges.append(self._edge(node_id, parallel_action_id, len(edges) + 1))
                edges.append(self._edge(parallel_action_id, join_id, len(edges) + 1))
                previous_node_id = join_id

            if self._is_document_step(step["text"]):
                object_id = f"uml_{index}_object"
                nodes.append(
                    {
                        "id": object_id,
                        "type": "OBJECT_NODE",
                        "umlElement": "ObjectNode",
                        "label": "Documento/Formulario",
                        "partition": self._partition_id(step["partition"]),
                    }
                )
                edges.append(self._edge(node_id, object_id, len(edges) + 1, edge_type="ObjectFlow"))

            if self._is_note_step(step["text"]):
                note_id = f"uml_{index}_note"
                nodes.append(
                    {
                        "id": note_id,
                        "type": "NOTE",
                        "umlElement": "Comment",
                        "label": "Nota aclaratoria",
                        "partition": self._partition_id(step["partition"]),
                    }
                )
                edges.append(self._edge(node_id, note_id, len(edges) + 1, edge_type="Annotation"))

        nodes.append(
            {
                "id": "activity_final",
                "type": "ACTIVITY_FINAL",
                "umlElement": "ActivityFinalNode",
                "label": "Fin",
                "partition": fallback_partition_id,
            }
        )
        edges.append(self._edge(previous_node_id, "activity_final", len(edges) + 1))

        return {
            "nodes": nodes,
            "edges": edges,
            "partitions": partitions,
            "metadata": {
                "umlVersion": self.UML_VERSION,
                "diagramType": "ActivityDiagram",
                "partitionElement": "ActivityPartition",
                "strategy": "rule_based_uml_activity_bootstrap",
                "businessContext": business_context,
            },
        }

    def _infer_step_type(self, sentence: str) -> str:
        lowered = sentence.lower()
        if re.search(r"\b(si|sino|else|aprobado|rechazado)\b", lowered):
            return "DECISION"
        if "paralelo" in lowered or "simult" in lowered:
            return "PARALLEL"
        return "TASK"

    def _infer_partition(self, sentence: str) -> str:
        lowered = sentence.lower()
        candidates = {
            "cliente": ["cliente", "solicitante", "usuario"],
            "ventas": ["ventas", "comercial", "asesor"],
            "soporte": ["soporte", "mesa de ayuda", "tecnico", "técnico"],
            "operaciones": ["operaciones", "operador", "funcionario"],
            "revision": ["revision", "revisión", "revisor", "gerente", "aprobador"],
            "sistema": ["sistema", "automatico", "automático", "notifica", "genera"],
        }
        for partition, keywords in candidates.items():
            if any(keyword in lowered for keyword in keywords):
                return partition
        return "negocio"

    def _build_partitions(self, steps: list[dict], business_context: str | None) -> list[dict]:
        partition_ids = []
        for step in steps:
            partition_id = self._partition_id(step["partition"])
            if partition_id not in partition_ids:
                partition_ids.append(partition_id)
        if not partition_ids:
            partition_ids.append("partition_negocio")

        return [
            {
                "id": partition_id,
                "name": self._partition_label(partition_id, business_context),
                "umlElement": "ActivityPartition",
            }
            for partition_id in partition_ids
        ]

    def _partition_id(self, partition: str) -> str:
        return f"partition_{partition.lower().replace(' ', '_')}"

    def _partition_label(self, partition_id: str, business_context: str | None) -> str:
        labels = {
            "partition_cliente": "Cliente",
            "partition_ventas": "Ventas",
            "partition_soporte": "Soporte",
            "partition_operaciones": "Operaciones",
            "partition_revision": "Revision / Aprobacion",
            "partition_sistema": "Sistema",
            "partition_negocio": "Negocio",
        }
        if partition_id == "partition_negocio" and business_context:
            return business_context.strip().title()[:48]
        return labels.get(partition_id, partition_id.replace("partition_", "").replace("_", " ").title())

    def _to_uml_node_type(self, step_type: str, text: str) -> str:
        if step_type == "DECISION":
            return "DECISION"
        if step_type == "PARALLEL":
            return "FORK"
        if self._is_signal_send_step(text):
            return "SEND_SIGNAL"
        if self._is_signal_receive_step(text):
            return "ACCEPT_SIGNAL"
        if self._is_document_step(text):
            return "ACTION"
        return "ACTION"

    def _uml_element_name(self, node_type: str) -> str:
        return {
            "INITIAL": "InitialNode",
            "ACTION": "Action",
            "DECISION": "DecisionNode",
            "MERGE": "MergeNode",
            "FORK": "ForkNode",
            "JOIN": "JoinNode",
            "ACTIVITY_FINAL": "ActivityFinalNode",
            "OBJECT_NODE": "ObjectNode",
            "SEND_SIGNAL": "SendSignalAction",
            "ACCEPT_SIGNAL": "AcceptEventAction",
            "NOTE": "Comment",
        }.get(node_type, "ActivityNode")

    def _edge(
        self,
        source: str,
        target: str,
        index: int,
        guard: str | None = None,
        edge_type: str = "ControlFlow",
    ) -> dict:
        edge = {
            "id": f"uml_edge_{index}",
            "source": source,
            "target": target,
            "type": edge_type,
        }
        if guard:
            edge["guard"] = guard
        return edge

    def _is_document_step(self, text: str) -> bool:
        lowered = text.lower()
        return any(keyword in lowered for keyword in ["documento", "documentos", "formulario", "archivo", "adjunto"])

    def _is_signal_send_step(self, text: str) -> bool:
        lowered = text.lower()
        return any(keyword in lowered for keyword in ["enviar señal", "envia señal", "envía señal", "notifica", "notificar", "mensaje"])

    def _is_signal_receive_step(self, text: str) -> bool:
        lowered = text.lower()
        return any(keyword in lowered for keyword in ["recibir señal", "recibe señal", "espera", "esperar", "evento externo"])

    def _is_note_step(self, text: str) -> bool:
        lowered = text.lower()
        return any(keyword in lowered for keyword in ["nota", "comentario", "observacion", "observación"])
