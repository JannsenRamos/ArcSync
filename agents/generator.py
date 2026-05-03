import logging
from integrations.watsonx_client import get_watsonx_client
from integrations.ibm_bob_client import IBMBobClient

logger = logging.getLogger(__name__)

# Fibonacci sequence for complexity scoring
FIBONACCI = [1, 2, 3, 5, 8, 13]


class GeneratorAgent:
    def __init__(self):
        self.watsonx = get_watsonx_client()

    def generate_spec(self, feature_name, raw_intent, context_anchors, repo_metadata=None):
        """Generates a grounded technical specification using Watsonx Granite + repository context."""

        # 1. Compute dynamic complexity
        complexity = self._compute_complexity(context_anchors, raw_intent)

        # 2. Build the context section for the prompt
        context_block = self._build_context_block(context_anchors, repo_metadata)

        # 3. Build the LLM prompt
        prompt = self._build_prompt(feature_name, raw_intent, context_block, repo_metadata, complexity)

        # 4. Call Watsonx Granite
        logger.info(f"Generating spec for '{feature_name}' with {len(context_anchors)} anchors...")
        llm_response = self.watsonx.generate(prompt, max_tokens=1500)

        # 5. Assemble the final specification
        spec = self._assemble_spec(feature_name, complexity, context_anchors, llm_response, repo_metadata)

        # 6. Log the generation event
        try:
            bob = IBMBobClient()
            bob.log_event("Specification Generated", {
                "feature": feature_name,
                "complexity": complexity,
                "anchors": len(context_anchors),
                "llm_tokens": len(llm_response.split())
            })
        except Exception:
            pass

        return spec

    def _compute_complexity(self, context_anchors, raw_intent):
        """Dynamic Fibonacci complexity based on real signals."""
        score = 0
        intent_lower = raw_intent.lower()
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Computing complexity for: '{raw_intent[:50]}...'")

        # Check for keywords first (strongest signal)
        complex_keywords = ['migration', 'refactor', 'integrate', 'payment', 'security', 'real-time', 'websocket', 'authentication', 'oauth']
        simple_keywords = ['add field', 'add boolean', 'add flag', 'update text', 'fix bug', 'add logging', 'change color']
        moderate_keywords = ['search', 'filter', 'upload', 'download', 'export', 'import']

        # Keyword-based scoring (most important)
        if any(k in intent_lower for k in complex_keywords):
            score += 3  # Major complexity indicators
        elif any(k in intent_lower for k in moderate_keywords):
            score += 1  # Moderate complexity
        
        if any(k in intent_lower for k in simple_keywords):
            score -= 2  # Explicitly simple tasks

        # Number of impacted files (secondary signal)
        num_files = len(context_anchors)
        if num_files >= 5:
            score += 2
        elif num_files >= 3:
            score += 1
        # Don't add points for 1-2 files (could be simple changes)

        # Check for architectural impacts (tertiary signal)
        has_model = any('model' in a.get('tags', []) for a in context_anchors)
        has_auth = any('auth' in a.get('tags', []) for a in context_anchors)
        has_route = any('route' in a.get('tags', []) for a in context_anchors)

        # Only add complexity if it's NOT a simple field addition
        if 'add field' not in intent_lower and 'add boolean' not in intent_lower:
            if has_model:
                score += 1  # Schema changes (reduced from 2)
            if has_auth:
                score += 2  # Auth changes = still risky
            if has_route and 'new' in intent_lower:
                score += 1  # Only if explicitly new routes

        # Map to Fibonacci [1, 2, 3, 5, 8, 13]
        # Score ranges:
        # -2 to 0 → 1 (Trivial)
        # 1 → 2 (Simple)
        # 2 → 3 (Easy)
        # 3-4 → 5 (Moderate)
        # 5-6 → 8 (Complex)
        # 7+ → 13 (Major)
        
        if score <= 0:
            return FIBONACCI[0]  # 1
        elif score == 1:
            return FIBONACCI[1]  # 2
        elif score == 2:
            return FIBONACCI[2]  # 3
        elif score <= 4:
            return FIBONACCI[3]  # 5
        elif score <= 6:
            return FIBONACCI[4]  # 8
        else:
            return FIBONACCI[5]  # 13

    def _build_context_block(self, context_anchors, repo_metadata):
        """Build a structured context block from matched anchors."""
        if not context_anchors:
            return "No matching files found in the repository."

        parts = []
        for i, anchor in enumerate(context_anchors[:5], 1):
            file_path = anchor.get("file", "Unknown")
            tags = ", ".join(anchor.get("tags", ["unknown"]))
            relevance = anchor.get("relevance", 0)
            snippet = anchor.get("snippet", "")
            endpoints = anchor.get("api_endpoints", [])

            part = f"**File {i}**: `{file_path}` [Tags: {tags}] (relevance: {relevance:.1f})"
            if snippet:
                # Show first few meaningful lines
                lines = [l for l in snippet.split('\n') if l.strip()][:8]
                code_preview = '\n'.join(lines)
                part += f"\n```\n{code_preview}\n```"
            if endpoints:
                ep_str = ", ".join(f"{e['method']} {e['path']}" for e in endpoints[:3])
                part += f"\nExisting endpoints: {ep_str}"
            parts.append(part)

        return "\n\n".join(parts)

    def _build_prompt(self, feature_name, raw_intent, context_block, repo_metadata, complexity):
        """Build a rich prompt for Watsonx Granite."""
        tech_stack = repo_metadata.get("tech_stack", "Unknown") if repo_metadata else "Unknown"
        database = repo_metadata.get("database", "Unknown") if repo_metadata else "Unknown"
        deps = repo_metadata.get("dependencies", {}) if repo_metadata else {}
        deps_str = ", ".join(list(deps.keys())[:15]) if deps else "None detected"

        prompt = f"""You are an expert software architect analyzing a codebase to assess feature feasibility. You are IBM Bob, a context-aware AI assistant that reads codebases and provides grounded technical recommendations.

## Repository Context
- **Tech Stack**: {tech_stack}
- **Database**: {database}
- **Key Dependencies**: {deps_str}

## Matched Repository Files
{context_block}

## Feature Request
- **Feature Name**: {feature_name}
- **Description**: {raw_intent}
- **Estimated Complexity**: {complexity}/13 (Fibonacci scale)

## Your Task
Analyze the repository context and provide a technical assessment. Use this EXACT format:

### Feasibility Verdict
**[FEASIBLE/FEASIBLE_WITH_CAVEATS/NOT_FEASIBLE]**

[Write 2-3 SHORT sentences explaining why. Each sentence on its own line. Reference specific files.]

### Risk Analysis
**Risk 1: [Title]**
[One sentence description referencing actual files]

**Risk 2: [Title]**
[One sentence description referencing actual files]

**Risk 3: [Title]**
[One sentence description referencing actual files]

### Proposed Changes
**1. [File/Module Name]**
[One sentence describing changes needed]

**2. [File/Module Name]**
[One sentence describing changes needed]

**3. [New File/Module]**
[One sentence describing where it should go and why]

### User Stories (Gherkin)
```gherkin
Feature: [Feature Name]
  Scenario: [Main scenario name]
    Given [precondition]
    When [action]
    Then [expected result]
    
  Scenario: [Error scenario name]
    Given [error condition]
    When [action]
    Then [error response]
```

### API Design
**Endpoint:** `[METHOD] /api/path`

**Request:**
```json
{{
  "field": "value",
  "nested": {{
    "data": "example"
  }}
}}
```

**Response:**
```json
{{
  "success": true,
  "data": {{
    "id": "value"
  }}
}}
```

CRITICAL FORMATTING RULES:
- Use double line breaks between sections
- Keep sentences SHORT (max 20 words)
- Each risk/change gets its own paragraph
- Use bold headers for each item
- Format ALL JSON with 2-space indentation
- Reference actual files from the repository context
"""
        return prompt

    def _assemble_spec(self, feature_name, complexity, context_anchors, llm_response, repo_metadata):
        """Assemble the final markdown specification."""
        tech_stack = repo_metadata.get("tech_stack", "Unknown") if repo_metadata else "Unknown"
        database = repo_metadata.get("database", "Unknown") if repo_metadata else "Unknown"

        # Build anchor list
        anchor_list = []
        for anchor in context_anchors[:5]:
            file_path = anchor.get("file", "Unknown file")
            tags = ", ".join(anchor.get("tags", []))
            relevance = anchor.get("relevance", 0.0)
            anchor_list.append(f"- `{file_path}` [{tags}] — Relevance: {relevance:.1f}")

        formatted_anchors = "\n".join(anchor_list) if anchor_list else "- No matching files found"

        # Get human-readable complexity interpretation
        complexity_label, complexity_desc, time_estimate = self._interpret_complexity(complexity)

        spec = f"""# 🚀 Feature Blueprint: {feature_name}

---

### 📊 Architectural Overview

| Metric | Value |
|--------|-------|
| **Complexity Score** | `{complexity}/13` — **{complexity_label}** |
| **Estimated Effort** | {time_estimate} |
| **Tech Stack** | {tech_stack} |
| **Database** | {database} |
| **Context Anchors** | {len(context_anchors)} files matched |

> **What does {complexity}/13 mean?** {complexity_desc}

---

### 🔍 Impacted Files
{formatted_anchors}

---

### 🧠 IBM Bob's Analysis

{llm_response}

---

*Generated by Arch-Sync — Grounded in your repository's reality via IBM Bob.*
"""
        return spec

    def _interpret_complexity(self, score):
        """Convert Fibonacci score to human-readable interpretation."""
        interpretations = {
            1: (
                "Trivial",
                "A simple change requiring minimal code modification. Usually a single file update with no architectural impact.",
                "~2-4 hours"
            ),
            2: (
                "Simple",
                "A straightforward feature touching 1-2 files. Low risk, no schema changes, follows existing patterns.",
                "~1 day"
            ),
            3: (
                "Easy",
                "A basic feature requiring 2-3 file changes. Minimal complexity, well-understood requirements.",
                "~1-2 days"
            ),
            5: (
                "Moderate",
                "A standard feature affecting multiple files or adding new routes. Some integration work needed.",
                "~2-3 days"
            ),
            8: (
                "Complex",
                "A significant feature requiring schema changes, external integrations, or touching critical systems like auth or payments.",
                "~1 week"
            ),
            13: (
                "Major",
                "A large-scale change affecting many files, requiring architectural decisions, migrations, or significant refactoring. Consider breaking into smaller tasks.",
                "~2+ weeks"
            )
        }
        
        return interpretations.get(score, ("Unknown", "Complexity could not be determined.", "Unknown"))