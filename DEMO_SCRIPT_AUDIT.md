# 🔍 Demo Video Script Audit Report

**Date:** 2026-05-03  
**Purpose:** Verify all claims in DEMO_VIDEO_SCRIPT.md against actual codebase implementation

---

## ✅ VERIFIED FEATURES (Exist in Code)

### 1. **ArcSync UI with Input Field**
- ✅ **Script Claims:** "Type into input field: `Add payment processing with Stripe`"
- ✅ **Code Evidence:** `static/index.html` lines 146-149 (feature name input) and lines 154-159 (intent textarea)
- ✅ **Status:** ACCURATE

### 2. **Generate Button**
- ✅ **Script Claims:** "Hit Generate button"
- ✅ **Code Evidence:** `static/index.html` lines 189-194 (`generate-btn` with `triggerArchSync()`)
- ✅ **Status:** ACCURATE

### 3. **IBM Bob Reading Repository**
- ✅ **Script Claims:** "Bob is reading the repository. Not a summary of it — the actual file tree, the models, the routes, the middleware."
- ✅ **Code Evidence:** 
  - `integrations/ibm_bob_client.py` lines 67-79 (`_get_code_files()`)
  - Lines 180-200 (`_read_key_files()` - reads actual file content)
  - Lines 202-212 (`_tag_files()` - tags models, routes, middleware)
- ✅ **Status:** ACCURATE

### 4. **Complexity Scoring (Fibonacci)**
- ✅ **Script Claims:** "A complexity estimate"
- ✅ **Code Evidence:** `agents/generator.py` lines 8, 48-114 (Fibonacci complexity calculation)
- ✅ **Status:** ACCURATE

### 5. **Architecture Section References Actual Files**
- ✅ **Script Claims:** "An architecture section that references the actual services in this repo"
- ✅ **Code Evidence:** 
  - `agents/generator.py` lines 116-140 (`_build_context_block()` - includes file paths and snippets)
  - Lines 245-252 (formatted anchors in spec output)
- ✅ **Status:** ACCURATE

### 6. **Watsonx Granite Generation**
- ✅ **Script Claims:** "Generating spec with Granite"
- ✅ **Code Evidence:** 
  - `integrations/watsonx_client.py` lines 23 (`model_id = "ibm/granite-3-8b-instruct"`)
  - Lines 50-106 (actual Watsonx API call)
- ✅ **Status:** ACCURATE

### 7. **IBM Bob Audit Logging**
- ✅ **Script Claims:** "Every action is logged through IBM Bob"
- ✅ **Code Evidence:** 
  - `integrations/ibm_bob_client.py` lines 251-266 (`log_event()` method)
  - `agents/generator.py` lines 34-44 (logs specification generation)
  - `agents/manager.py` lines 38-44, 51-55 (logs retrieval and delivery)
- ✅ **Status:** ACCURATE

### 8. **Repository Upload Feature**
- ✅ **Script Claims:** "Upload ZIP" button mentioned in pre-recording checklist
- ✅ **Code Evidence:** 
  - `static/index.html` lines 114-118 (Upload ZIP button)
  - `static/script.js` lines 76-120 (`uploadRepository()` function)
- ✅ **Status:** ACCURATE

### 9. **Tech Stack Detection**
- ✅ **Script Claims:** Shows tech stack badges
- ✅ **Code Evidence:** 
  - `integrations/ibm_bob_client.py` lines 81-122 (`_detect_tech_stack()`)
  - `static/index.html` lines 120-123 (tech stack, db, files, API badges)
- ✅ **Status:** ACCURATE

### 10. **API Endpoint Detection**
- ✅ **Script Claims:** References to "payments router" and existing endpoints
- ✅ **Code Evidence:** `integrations/ibm_bob_client.py` lines 214-241 (`_detect_api_patterns()`)
- ✅ **Status:** ACCURATE

---

## ⚠️ PARTIALLY ACCURATE CLAIMS

### 1. **"Three Open Questions the PM Needs to Answer"**
- ⚠️ **Script Claims:** "And three open questions the PM needs to answer before engineering can even start"
- ⚠️ **Code Evidence:** The prompt in `agents/generator.py` lines 142-236 does NOT explicitly request "open questions"
- ⚠️ **Reality:** The LLM might generate questions, but it's not a structured output field
- ⚠️ **Recommendation:** Either:
  - Remove this claim from the script, OR
  - Add "Open Questions" section to the prompt template

### 2. **"Acceptance Criteria"**
- ⚠️ **Script Claims:** "User stories. Acceptance criteria."
- ⚠️ **Code Evidence:** 
  - User Stories: ✅ Explicitly requested in prompt (lines 192-204)
  - Acceptance Criteria: ❌ NOT explicitly requested in prompt
- ⚠️ **Reality:** The prompt asks for "User Stories (Gherkin)" but not separate "Acceptance Criteria"
- ⚠️ **Recommendation:** Either:
  - Change script to say "User stories in Gherkin format", OR
  - Add "Acceptance Criteria" section to prompt template

---

## ❌ MISLEADING OR UNCLEAR CLAIMS

### 1. **"IBM Bob Interface"**
- ❌ **Script Claims:** "Open IBM Bob interface. Show the repo loaded with full context."
- ❌ **Reality:** There is NO separate "IBM Bob interface" to open
- ❌ **What Actually Exists:**
  - IBM Bob is a backend client (`integrations/ibm_bob_client.py`)
  - The UI shows Bob's status in the header (line 82-85 in `index.html`)
  - Audit logs are in `logs/ibm_bob_audit/` directory
- ❌ **Recommendation:** Change script to:
  - "Show the IBM Bob status indicator in the header"
  - "Show the audit log file in the logs directory"
  - "Show the browser DevTools Network tab during generation"

### 2. **"Bob Also Wrote the Generation Pipeline Itself"**
- ❌ **Script Claims:** "Bob also wrote the generation pipeline itself. Here's the endpoint boilerplate Bob produced during the build."
- ❌ **Reality:** This is MISLEADING
- ❌ **What Actually Happened:** 
  - IBM Bob (the IDE assistant) may have helped write code during development
  - But the current codebase doesn't show "Bob-generated" markers
  - The generation pipeline was written BY YOU (the developer), possibly WITH Bob's assistance
- ❌ **Recommendation:** Rephrase to:
  - "I used IBM Bob during development to help write the generation pipeline"
  - "Here's code I wrote with Bob's assistance during the build"
  - Be honest: "Bob helped me write this, but I reviewed and refined it"

### 3. **"Notification Service and Order Event System"**
- ⚠️ **Script Claims:** "The architecture section now references the notification service and the order event system — because they're in the repo"
- ⚠️ **Reality:** The sample e-commerce repo (`sample_repos/ecommerce-api/`) does NOT have:
  - A notification service
  - An order event system
- ⚠️ **What It Has:**
  - `src/models/order.js`
  - `src/routes/orders.js`
  - Basic CRUD operations
- ⚠️ **Recommendation:** Use a more accurate second demo input like:
  - "Add order status tracking" (references existing Order model)
  - "Add product search functionality" (references Product model)
  - "Add user profile management" (references User model)

---

## 🎯 RECOMMENDED SCRIPT FIXES

### Fix #1: Remove "Open Questions" Claim
**Current:**
> "And three open questions the PM needs to answer before engineering can even start."

**Recommended:**
> "Edge cases it found by reading the code. A complexity estimate. And a feasibility verdict with specific risks."

### Fix #2: Clarify "Acceptance Criteria"
**Current:**
> "User stories. Acceptance criteria."

**Recommended:**
> "User stories in Gherkin format. API design with request/response examples."

### Fix #3: Replace "IBM Bob Interface" Section
**Current:**
> "Open IBM Bob interface. Show the repo loaded with full context."

**Recommended:**
> "Show IBM Bob's status in the header — it's already scanned the repository. Watch the browser's Network tab to see the live API call to Watsonx Granite."

### Fix #4: Honest "Bob Wrote Code" Claim
**Current:**
> "Bob also wrote the generation pipeline itself. Here's the endpoint boilerplate Bob produced during the build. I reviewed it, corrected one import, and it ran."

**Recommended:**
> "I built this generation pipeline with IBM Bob's assistance during development. Here's an example of code Bob helped me write — I reviewed it, refined it, and integrated it into the system."

### Fix #5: Accurate Second Demo Input
**Current:**
> "Add email notifications when an order ships"

**Recommended (choose one):**
> "Add order status tracking with history"
> "Add product search with filters"
> "Add user authentication with JWT"

---

## 📊 AUDIT SUMMARY

| Category | Count | Percentage |
|----------|-------|------------|
| ✅ Fully Accurate | 10 | 67% |
| ⚠️ Partially Accurate | 2 | 13% |
| ❌ Misleading/Unclear | 3 | 20% |
| **Total Claims Audited** | **15** | **100%** |

---

## 🚨 CRITICAL ISSUES TO FIX BEFORE RECORDING

### Priority 1 (Must Fix)
1. ❌ **Remove "IBM Bob Interface" claim** — No such interface exists
2. ❌ **Rephrase "Bob wrote code" claim** — Be honest about Bob's role
3. ⚠️ **Change second demo input** — Current one references non-existent services

### Priority 2 (Should Fix)
4. ⚠️ **Remove "open questions" claim** — Not in current output
5. ⚠️ **Change "acceptance criteria" to "Gherkin scenarios"** — More accurate

### Priority 3 (Nice to Have)
6. Consider adding "Open Questions" section to prompt if you want to keep that claim
7. Consider adding "Acceptance Criteria" section to prompt if you want to keep that claim

---

## ✅ WHAT YOU CAN CONFIDENTLY SHOW

1. ✅ **Live generation** — Type input, click generate, watch it work
2. ✅ **IBM Bob reading files** — Show the audit log with file paths
3. ✅ **Complexity scoring** — Show the Fibonacci gauge updating
4. ✅ **File references** — Show actual file paths in the output
5. ✅ **Watsonx Granite** — Show Network tab with API call
6. ✅ **Two different inputs** — Both work, both reference different files
7. ✅ **Tech stack detection** — Show badges updating
8. ✅ **Repository upload** — Upload a ZIP, watch it index

---

## 🎬 RECOMMENDED DEMO FLOW

### [0:00-0:20] Hook
✅ Keep as-is (Slack message is perfect)

### [0:20-0:50] First Demo
✅ Keep as-is (works perfectly)

### [0:50-1:50] IBM Bob Section
❌ **CHANGE THIS:**
- Don't say "Open IBM Bob interface" (doesn't exist)
- Instead: "Show IBM Bob status indicator, audit logs, and Network tab"
- Show: Browser DevTools → Network → API call to Watsonx
- Show: File explorer → `logs/ibm_bob_audit/` → Open latest `.jsonl` file
- Explain: "Bob scanned the repo, logged everything, and passed context to Granite"

### [1:50-2:30] Second Demo
⚠️ **CHANGE INPUT TO:**
- "Add order status tracking with history" (references existing Order model)
- OR "Add product search with filters" (references existing Product model)

---

## 📝 FINAL RECOMMENDATION

**The demo script is 67% accurate but has 3 critical issues that will hurt credibility:**

1. The "IBM Bob interface" doesn't exist as described
2. The "Bob wrote code" claim is misleading
3. The second demo input references non-existent services

**Fix these 3 issues and your demo will be honest, accurate, and impressive.**

The technology is real. The features work. Just describe them accurately.
