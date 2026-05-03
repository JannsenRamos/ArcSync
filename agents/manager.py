from agents.generator import GeneratorAgent
from core.retriever import RetrieverAgent
from core.indexer import CoreIndexer
from integrations.ibm_bob_client import IBMBobClient
import logging

logger = logging.getLogger(__name__)


class ManagerAgent:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.bob_client = IBMBobClient(repo_path=repo_path)
        self.indexer = CoreIndexer()
        self.generator = GeneratorAgent()

        # Step 1: Initialize the index with Bob's metadata
        logger.info(f"Indexing repository: {repo_path}")
        metadata = self.bob_client.get_repository_context()
        self.indexer.index_repository(metadata)

        # Step 2: Initialize the retriever pointing to that index
        self.retriever = RetrieverAgent()

        logger.info(
            f"ManagerAgent ready — {len(metadata['directory_map'])} files indexed, "
            f"stack: {metadata['tech_stack']}, db: {metadata['database']}"
        )

    def orchestrate_spec_request(self, feature_name, raw_intent):
        """Orchestrate the full spec generation pipeline."""
        # 1. Retrieve context anchors
        context_anchors = self.retriever.get_prompt_context(raw_intent)

        # 2. Get repo-level metadata
        repo_metadata = self.retriever.get_metadata()

        # 3. Log the retrieval event
        self.bob_client.log_event("Context Retrieval", {
            "feature": feature_name,
            "intent": raw_intent,
            "anchors_found": len(context_anchors),
            "anchor_files": [a['file'] for a in context_anchors]
        })

        # 4. Generate the specification with LLM
        spec = self.generator.generate_spec(
            feature_name, raw_intent, context_anchors, repo_metadata
        )

        # 5. Log the completion
        self.bob_client.log_event("Specification Delivered", {
            "feature": feature_name,
            "spec_length": len(spec),
        })

        return spec