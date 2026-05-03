from integrations.ibm_bob_client import IBMBobClient


class ContextAgent:
    """
    Acts as the liaison to the IBM Bob Layer.
    Specializes in translating repository metadata into technical constraints.
    """
    def __init__(self, repo_path="."):
        self.bob_client = IBMBobClient(repo_path=repo_path)

    def get_grounding_constraints(self):
        """
        Fetches fresh metadata from IBM Bob to prevent architectural drift.
        """
        metadata = self.bob_client.get_repository_context()

        constraints = {
            "tech_stack": metadata.get("tech_stack", "Unknown"),
            "database": metadata.get("database", "Unknown"),
            "file_count": len(metadata.get("directory_map", [])),
            "dependencies": metadata.get("dependencies", {}),
            "api_endpoints": len(metadata.get("api_patterns", [])),
        }
        return constraints