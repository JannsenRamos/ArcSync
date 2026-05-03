import os
import logging
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class WatsonxClient:
    """
    Direct REST API client for IBM watsonx.ai Foundation Models.
    Uses the HTTP API instead of the SDK to avoid numpy/pandas dependency issues.
    Uses Granite 3 8B Instruct for grounded spec generation.
    """

    def __init__(self):
        self.api_key = os.getenv("IBM_API_KEY", "").strip()
        self.project_id = os.getenv("WATSONX_PROJECT_ID", "").strip()
        self.url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com").strip()
        self.model_id = "ibm/granite-3-8b-instruct"
        self._token = None
        self._initialized = False

    def _get_iam_token(self):
        """Get an IAM access token from IBM Cloud."""
        if not self.api_key:
            return None

        try:
            response = requests.post(
                "https://iam.cloud.ibm.com/identity/token",
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": self.api_key
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            response.raise_for_status()
            self._token = response.json()["access_token"]
            logger.info("IAM token obtained successfully.")
            return self._token
        except Exception as e:
            logger.error(f"Failed to get IAM token: {e}")
            return None

    def generate(self, prompt: str, max_tokens: int = 1500) -> str:
        """
        Generate text using IBM Granite via watsonx.ai REST API.
        Falls back to a template-based response if Watsonx is unavailable.
        """
        if not self.api_key or not self.project_id:
            logger.warning("Watsonx credentials not configured. Using fallback generation.")
            return self._fallback_generate(prompt)

        # Get fresh token
        token = self._get_iam_token()
        if not token:
            return self._fallback_generate(prompt)

        try:
            url = f"{self.url}/ml/v1/text/generation?version=2024-05-31"

            payload = {
                "model_id": self.model_id,
                "input": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "top_k": 50,
                    "repetition_penalty": 1.1,
                    "stop_sequences": []
                },
                "project_id": self.project_id
            }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            logger.info(f"Sending prompt to Watsonx ({len(prompt)} chars, model={self.model_id})...")
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()

            result = response.json()
            generated_text = result.get("results", [{}])[0].get("generated_text", "")

            if not generated_text:
                logger.warning("Empty response from Watsonx.")
                return self._fallback_generate(prompt)

            logger.info(f"Watsonx response received ({len(generated_text)} chars).")
            return generated_text

        except requests.exceptions.HTTPError as e:
            logger.error(f"Watsonx HTTP error: {e.response.status_code} - {e.response.text}")
            return self._fallback_generate(prompt)
        except Exception as e:
            logger.error(f"Watsonx generation failed: {e}")
            return self._fallback_generate(prompt)

    def _fallback_generate(self, prompt: str) -> str:
        """Intelligent fallback when Watsonx is unavailable."""
        return """### Feasibility Verdict
**FEASIBLE_WITH_CAVEATS**

This feature can be implemented within the existing architecture.

Some modifications to existing modules will be required.

The codebase structure supports this type of enhancement.

### Risk Analysis
**Risk 1: Schema Changes**
New fields or collections may need to be added to the data layer.

**Risk 2: Integration Complexity**
Existing middleware and auth patterns should be carefully reused.

**Risk 3: Testing Coverage**
New routes and business logic will need comprehensive test coverage.

### Proposed Changes
**1. Route Handlers (`src/routes/`)**
Add new route handlers following existing patterns in the routes directory.

**2. Data Models (`src/models/`)**
Extend models with required fields to support the new feature.

**3. Middleware (`src/middleware/`)**
Add middleware for any new business logic or validation.

### User Stories (Gherkin)
```gherkin
Feature: New Feature Implementation
  Scenario: Happy path
    Given the system is properly configured
    When the user performs the main action
    Then the system responds successfully
    
  Scenario: Error handling
    Given the system encounters invalid input
    When the user attempts the action
    Then the system returns an appropriate error
```

### API Design
**Endpoint:** `POST /api/resource`

**Request:**
```json
{
  "field": "value",
  "nested": {
    "data": "example"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "generated_id",
    "field": "value"
  }
}
```

---
*Note: IBM Watsonx was unavailable. This is a template-based analysis. Connect Watsonx for AI-powered recommendations.*"""


# Singleton instance
_client = None

def get_watsonx_client() -> WatsonxClient:
    global _client
    if _client is None:
        _client = WatsonxClient()
    return _client
