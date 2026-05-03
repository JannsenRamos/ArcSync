import json
from pathlib import Path


class CoreIndexer:
    """
    Transforms IBM Bob metadata into a searchable index for Hybrid RAG.
    Satisfies FR2: Repository Context Injection.
    """
    def __init__(self, index_path="data/index"):
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.vector_store = {}

    def index_repository(self, bob_metadata):
        """
        Processes metadata from IBM Bob to create an architectural blueprint.
        Now indexes file content, tags, and structural information.
        """
        repo_map = bob_metadata.get("directory_map", [])
        tech_stack = bob_metadata.get("tech_stack", "Generic")
        file_contents = bob_metadata.get("file_contents", {})
        file_tags = bob_metadata.get("file_tags", {})
        api_patterns = bob_metadata.get("api_patterns", [])
        database = bob_metadata.get("database", "Unknown")
        dependencies = bob_metadata.get("dependencies", {})

        for file_path in repo_map:
            # Assign weight based on architectural significance
            weight = 1.0
            tags = file_tags.get(file_path, ['source'])

            # Models/schemas get highest weight
            if 'model' in tags:
                weight = 3.0
            elif 'route' in tags:
                weight = 2.5
            elif 'auth' in tags:
                weight = 2.5
            elif 'middleware' in tags:
                weight = 2.0
            elif 'config' in tags or 'database' in tags:
                weight = 1.8
            elif 'service' in tags:
                weight = 1.5

            # Extract content snippet
            content = file_contents.get(file_path, "")
            snippet = content[:500] if content else ""

            # Find API patterns for this file
            file_apis = [
                p for p in api_patterns
                if p.get("file") == file_path
            ]

            self.vector_store[file_path] = {
                "path": file_path,
                "stack": tech_stack,
                "database": database,
                "priority_weight": weight,
                "tags": tags,
                "content_snippet": snippet,
                "api_endpoints": file_apis,
                # Build a searchable text blob for keyword matching
                "searchable_text": self._build_searchable_text(file_path, content, tags)
            }

        # Store metadata summary
        self.vector_store["__metadata__"] = {
            "tech_stack": tech_stack,
            "database": database,
            "total_files": len(repo_map),
            "dependencies": dependencies
        }

        self._save_index()
        return len(self.vector_store) - 1  # Exclude metadata entry

    def _build_searchable_text(self, file_path, content, tags):
        """Build a text blob for keyword/synonym searching."""
        parts = [file_path.lower()]
        parts.extend(tags)

        if content:
            # Extract meaningful words from content (variable names, function names)
            words = []
            for line in content.split('\n')[:50]:
                line = line.strip()
                if line and not line.startswith(('#', '//', '/*', '*', '"""', "'''")):
                    words.append(line.lower())
            parts.extend(words)

        return ' '.join(parts)

    def _save_index(self):
        """Persists the index for rapid retrieval under 30 seconds."""
        with open(self.index_path / "repo_index.json", "w") as f:
            json.dump(self.vector_store, f, indent=2)