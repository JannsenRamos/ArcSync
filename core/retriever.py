import json
from pathlib import Path

# Synonym map for smarter intent matching
SYNONYMS = {
    "auth": ["authentication", "login", "signup", "register", "session", "jwt", "oauth", "token", "password", "credential", "permission", "role", "access"],
    "payment": ["pay", "stripe", "checkout", "billing", "invoice", "transaction", "charge", "subscription", "pricing", "wallet"],
    "user": ["account", "profile", "member", "customer", "admin", "role"],
    "product": ["item", "catalog", "listing", "inventory", "stock", "sku", "merchandise"],
    "order": ["cart", "purchase", "checkout", "shipping", "delivery", "tracking", "fulfillment"],
    "search": ["filter", "query", "find", "browse", "sort", "pagination", "autocomplete"],
    "api": ["endpoint", "route", "rest", "graphql", "controller", "handler"],
    "database": ["db", "schema", "model", "migration", "table", "collection", "index"],
    "notification": ["email", "sms", "push", "alert", "message", "webhook"],
    "upload": ["file", "image", "media", "attachment", "storage", "s3", "blob"],
    "test": ["testing", "spec", "unit", "integration", "e2e", "coverage"],
    "config": ["configuration", "setting", "environment", "env", "constant"],
    "cache": ["caching", "redis", "memcached", "session"],
    "security": ["cors", "helmet", "rate-limit", "sanitize", "validate", "xss", "csrf"],
    "export": ["download", "csv", "pdf", "report", "analytics"],
    "review": ["rating", "feedback", "comment", "star"],
}


class RetrieverAgent:
    """
    Orchestrates the Hybrid RAG process to map user intent against repository context.
    Satisfies Success Metric: Zero Framework Hallucinations.
    """
    def __init__(self, index_path="data/index/repo_index.json"):
        self.index_path = Path(index_path)
        self.index = self._load_index()

    def _load_index(self):
        """Loads the grounded architectural anchors."""
        if not self.index_path.exists():
            return {}
        with open(self.index_path, "r") as f:
            return json.load(f)

    def _expand_keywords(self, intent):
        """Expand intent keywords with synonyms for better matching."""
        words = intent.lower().split()
        expanded = set(words)

        for word in words:
            # Check if word is in synonym keys
            if word in SYNONYMS:
                expanded.update(SYNONYMS[word])
            # Check if word appears in synonym values
            for key, synonyms in SYNONYMS.items():
                if word in synonyms:
                    expanded.add(key)
                    expanded.update(synonyms)

        return list(expanded)

    def retrieve_relevant_anchors(self, user_intent):
        """
        Maps natural language intake (FR1) to repository metadata (FR2).
        Uses synonym expansion and content-based matching.
        """
        expanded_keywords = self._expand_keywords(user_intent)
        matched_anchors = []

        for path, metadata in self.index.items():
            if path == "__metadata__":
                continue

            score = 0.0
            searchable = metadata.get("searchable_text", path.lower())
            base_weight = metadata.get("priority_weight", 1.0)

            # Score based on keyword matches in searchable text
            for keyword in expanded_keywords:
                if keyword in searchable:
                    score += 1.0
                if keyword in path.lower():
                    score += 0.5  # Bonus for filename match

            # Score based on API endpoint matches
            for endpoint in metadata.get("api_endpoints", []):
                endpoint_text = f"{endpoint.get('method', '')} {endpoint.get('path', '')}".lower()
                for keyword in expanded_keywords:
                    if keyword in endpoint_text:
                        score += 1.5

            if score > 0:
                matched_anchors.append({
                    "file": path,
                    "relevance": score * base_weight,
                    "stack": metadata.get("stack"),
                    "tags": metadata.get("tags", []),
                    "content_snippet": metadata.get("content_snippet", ""),
                    "api_endpoints": metadata.get("api_endpoints", [])
                })

        # Sort by relevance
        return sorted(matched_anchors, key=lambda x: x['relevance'], reverse=True)

    def get_prompt_context(self, user_intent):
        """
        Returns a list of anchor dictionaries for the Generator Agent.
        Each anchor contains: file, snippet, relevance, tags, and endpoints.
        """
        anchors = self.retrieve_relevant_anchors(user_intent)
        if not anchors:
            return []

        # Return top 5 most relevant anchors with rich context
        result = []
        for a in anchors[:5]:
            result.append({
                "file": a['file'],
                "snippet": a.get('content_snippet', '')[:300],
                "relevance": a['relevance'],
                "tags": a.get('tags', []),
                "api_endpoints": a.get('api_endpoints', []),
                "stack": a.get('stack', 'Unknown')
            })

        return result

    def get_metadata(self):
        """Get repository-level metadata."""
        return self.index.get("__metadata__", {})