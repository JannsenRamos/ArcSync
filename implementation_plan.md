# ArcSync Hackathon Upgrade — Implementation Plan

Transform ArcSync from a template-filling MVP into a demo-ready product where **Watsonx Granite actually reasons about a codebase** and delivers a feasibility verdict + grounded technical specification.

## User Review Required

> [!IMPORTANT]
> **You need your Watsonx Project ID.** Go to your watsonx.ai project → **Manage** tab → **General** → **Details** section. Copy the Project ID and add it to `.env` as `WATSONX_PROJECT_ID=...`. Also add `WATSONX_URL=https://us-south.ml.cloud.ibm.com` (or your region's URL).

> [!IMPORTANT]
> **Sample demo project:** I'll create a realistic sample project (`sample_repos/ecommerce-api/`) — a Node.js Express + MongoDB e-commerce API with models, routes, and schemas. This gives a compelling demo target that's different from ArcSync itself.

## Proposed Changes

### Component 1: Sample Demo Repository

Create a realistic, small codebase that ArcSync can analyze during the demo.

#### [NEW] `sample_repos/ecommerce-api/` (multiple files)
- `package.json` — Node.js/Express dependencies
- `src/models/product.js` — Mongoose product schema
- `src/models/user.js` — Mongoose user schema
- `src/routes/products.js` — CRUD API routes
- `src/routes/auth.js` — Authentication routes
- `src/middleware/auth.js` — JWT middleware
- `src/config/db.js` — MongoDB connection
- `README.md` — Project documentation

This gives ArcSync a **realistic, non-trivial repo** to analyze with multiple patterns (REST, JWT auth, Mongoose, etc.).

---

### Component 2: Watsonx LLM Integration

Replace simulated reasoning with real Granite model calls.

#### [MODIFY] [.env](file:///c:/Users/Lenovo/Desktop/ArcSync/.env)
- Add `WATSONX_PROJECT_ID` and `WATSONX_URL` placeholders

#### [NEW] `integrations/watsonx_client.py`
- Wraps `ibm-watsonx-ai` SDK's `ModelInference` class
- Uses `ibm/granite-3-8b-instruct` model
- Exposes a `generate(prompt, max_tokens)` method
- Handles errors and timeouts gracefully
- Logs all calls to the IBM Bob audit trail

---

### Component 3: Intelligent Spec Generation

Make the generator produce real, context-grounded output.

#### [MODIFY] [generator.py](file:///c:/Users/Lenovo/Desktop/ArcSync/agents/generator.py)
- Call Watsonx to generate:
  - **Feasibility Verdict** (FEASIBLE / FEASIBLE WITH CAVEATS / NOT FEASIBLE)
  - **Risk Analysis** based on matched files
  - **Gherkin User Stories**
  - **Proposed Schema/API Changes**
  - **Dynamic Fibonacci Complexity** based on number of impacted areas, new modules needed, schema changes
- Build a rich prompt that injects repository context (file list, tech stack, matched anchors)

---

### Component 4: Smarter Repository Analysis

Improve how Bob understands the target repo.

#### [MODIFY] [ibm_bob_client.py](file:///c:/Users/Lenovo/Desktop/ArcSync/integrations/ibm_bob_client.py)
- Better tech stack detection: check `package.json`, `pom.xml`, `go.mod`, `Cargo.toml`, `Gemfile`, etc.
- Read actual file content (first 100 lines) for key files (models, routes, schemas)
- Extract dependency list from `package.json` / `requirements.txt`
- Detect database type from code patterns (Mongoose → MongoDB, SQLAlchemy → SQL, etc.)

#### [MODIFY] [retriever.py](file:///c:/Users/Lenovo/Desktop/ArcSync/core/retriever.py)
- Add synonym/alias matching (auth → authentication, login, session, jwt, oauth)
- Search file **content**, not just filenames
- Boost relevance for models/schemas/routes

#### [MODIFY] [indexer.py](file:///c:/Users/Lenovo/Desktop/ArcSync/core/indexer.py)
- Index file content snippets (first 50 lines of each file)
- Detect and tag file types (model, route, middleware, config, test)
- Store richer metadata per file

---

### Component 5: HTML Dashboard — Full Wiring

Make the HTML UI fully functional with loading states and dynamic updates.

#### [MODIFY] [index.html](file:///c:/Users/Lenovo/Desktop/ArcSync/static/index.html)
- Fix `onclick` on "Process Requirements" button
- Move JS into proper `<script>` tags
- Add loading spinner/stepper animation during generation
- Add a "Feature Name" input field
- Add a **Feasibility Verdict** badge (green/yellow/red)
- Add a **Generated Spec** panel that renders markdown output
- Add a **Repo Selector** dropdown (ArcSync, Sample E-Commerce API)
- Update complexity gauge dynamically (not hardcoded 8/13)

#### [MODIFY] [script.js](file:///c:/Users/Lenovo/Desktop/ArcSync/static/script.js)
- Rewrite to handle full API workflow
- Add loading state management
- Parse and render markdown spec output
- Update gauge SVG dynamically
- Handle error states

#### [MODIFY] [server.py](file:///c:/Users/Lenovo/Desktop/ArcSync/static/server.py)
- Add endpoint to list available repos (`GET /api/v1/repos`)
- Modify generate endpoint to accept `repo_path` parameter
- Re-initialize agents with selected repo path
- Improve response parsing to extract all new fields (verdict, stories, etc.)

---

### Component 6: Audit & Export

#### [MODIFY] [ibm_bob_client.py](file:///c:/Users/Lenovo/Desktop/ArcSync/integrations/ibm_bob_client.py)
- Log richer audit events (LLM prompts, responses, latency)
- Generate a formatted audit report on export

#### [MODIFY] [server.py](file:///c:/Users/Lenovo/Desktop/ArcSync/static/server.py)
- Add `GET /api/v1/export` endpoint that returns the JSONL audit file

---

### Component 7: Dependencies

#### [MODIFY] [requirements.txt](file:///c:/Users/Lenovo/Desktop/ArcSync/requirements.txt)
- Add `ibm-watsonx-ai` (the actual SDK)
- Add `uvicorn` and `fastapi` (for the server)
- Add `pydantic`
- Remove `ibm-watson-machine-learning` (deprecated, replaced by `ibm-watsonx-ai`)

---

## Verification Plan

### Automated Tests
1. Run `python test_workflow.py` — ensure existing tests still pass
2. Start FastAPI server: `python static/server.py`
3. Use browser to navigate to `http://localhost:8000`
4. Enter a feature request (e.g., "Add Stripe payment integration") targeting the sample e-commerce repo
5. Verify:
   - Loading animation appears
   - Complexity gauge updates dynamically
   - Feasibility verdict shows (green/yellow/red)
   - Structural anchors show real files from the sample repo
   - Generated spec includes Gherkin stories and API suggestions
   - Audit log is generated in `logs/ibm_bob_audit/`

### Manual Verification
- Export IBM Bob session report via the FAB button
- Verify the JSONL contains meaningful audit entries
