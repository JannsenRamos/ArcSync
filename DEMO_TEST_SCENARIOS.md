# 🧪 ArcSync Demo Video Test Scenarios

## 📋 Overview
Comprehensive test scenarios for the demo video using the sample e-commerce API repository. These scenarios cover normal operations, edge cases, and potential failure points to ensure a smooth demo.

---

## 🎯 Primary Demo Scenarios (For Video)

### Scenario 1: Payment Integration Feature (Main Demo)
**Feature Request:** "Add payment processing with Stripe"

**Expected Behavior:**
- ✅ Analyzes existing Order model with payment fields
- ✅ References existing Stripe dependency in package.json
- ✅ Suggests middleware patterns consistent with auth.js
- ✅ Identifies payment-related routes needed
- ✅ Complexity score: 8/13 (moderate)
- ✅ Generation time: < 30 seconds

**Key Files Retrieved:**
- `src/models/order.js` (paymentMethod, paymentResult fields)
- `src/routes/orders.js`
- `package.json` (Stripe SDK already present)
- `src/middleware/auth.js` (pattern reference)

**IBM Bob Audit Trail:**
- Repository scan logged
- File indexing operations tracked
- Retrieval queries recorded
- Generation metadata captured

---

### Scenario 2: User Wishlist Enhancement
**Feature Request:** "Add wishlist management with notifications"

**Expected Behavior:**
- ✅ Detects existing wishlist field in User model
- ✅ Suggests CRUD operations for wishlist
- ✅ References Product model for population
- ✅ Complexity score: 5/13 (simple)
- ✅ Identifies notification integration points

**Key Files Retrieved:**
- `src/models/user.js` (wishlist array already exists)
- `src/models/product.js`
- `src/routes/auth.js` (GET /me already populates wishlist)

---

### Scenario 3: Product Review System Enhancement
**Feature Request:** "Add review moderation and helpful votes"

**Expected Behavior:**
- ✅ Analyzes existing review schema in Product model
- ✅ Suggests extending reviewSchema with new fields
- ✅ References existing review route pattern
- ✅ Complexity score: 5/13 (simple)
- ✅ Maintains consistency with current architecture

**Key Files Retrieved:**
- `src/models/product.js` (reviewSchema, updateAverageRating method)
- `src/routes/products.js` (POST /:id/reviews endpoint)
- `src/middleware/auth.js` (authentication pattern)

---

## 🔍 Edge Case Test Scenarios

### Edge Case 1: Empty Repository
**Setup:** Point to an empty directory

**Expected Behavior:**
- ⚠️ Graceful error: "No code files found in repository"
- ⚠️ Suggests checking repository path
- ⚠️ IBM Bob logs the failed scan attempt
- ⚠️ No generation attempted

**Test Command:**
```bash
mkdir empty_repo
# Point ArcSync to empty_repo/
```

---

### Edge Case 2: Non-Existent Repository Path
**Setup:** Provide invalid path

**Expected Behavior:**
- ⚠️ Error: "Repository path does not exist"
- ⚠️ Validation before indexing
- ⚠️ IBM Bob logs validation failure
- ⚠️ Clear error message to user

**Test Input:**
```
Repository: /invalid/path/to/repo
```

---

### Edge Case 3: Incompatible Technology Request
**Feature Request:** "Add GraphQL API with Apollo Server"

**Expected Behavior:**
- ✅ Detects REST architecture (Express routes)
- ⚠️ Warns about architectural mismatch
- ✅ Suggests REST-compatible alternative OR
- ✅ Provides migration considerations
- ✅ Complexity score: 13/13 (major architectural change)

**Key Detection:**
- Express.js framework detected
- RESTful route patterns identified
- No GraphQL dependencies in package.json

---

### Edge Case 4: Vague Feature Request
**Feature Request:** "Make it better"

**Expected Behavior:**
- ⚠️ Requests clarification
- ✅ Suggests specific improvement areas based on codebase analysis:
  - Add input validation (Joi already in dependencies)
  - Implement rate limiting (express-rate-limit present)
  - Add API documentation
  - Enhance error handling

---

### Edge Case 5: Already Implemented Feature
**Feature Request:** "Add JWT authentication"

**Expected Behavior:**
- ✅ Detects existing JWT implementation
- ✅ Shows current implementation details:
  - JWT in package.json
  - generateAuthToken method in User model
  - authenticate middleware exists
- ✅ Suggests enhancements instead:
  - Refresh token mechanism
  - Token blacklisting
  - Multi-factor authentication
- ✅ Complexity score: 3/13 (enhancement only)

---

### Edge Case 6: Large Repository (Performance Test)
**Setup:** Repository with 100+ files

**Expected Behavior:**
- ✅ Efficient indexing with progress indicator
- ✅ Selective retrieval (not all files loaded)
- ✅ Generation time: < 45 seconds
- ✅ IBM Bob logs all operations without performance degradation
- ✅ Memory usage remains reasonable

**Performance Metrics:**
- Indexing: < 10 seconds
- Retrieval: < 5 seconds
- Generation: < 30 seconds
- Total: < 45 seconds

---

### Edge Case 7: Binary Files in Repository
**Setup:** Repository with images, PDFs, compiled files

**Expected Behavior:**
- ✅ Skips binary files during indexing
- ✅ Focuses on code files (.js, .py, .java, etc.)
- ✅ Logs skipped files in IBM Bob audit
- ✅ No errors or crashes

**Test Files:**
- `images/logo.png`
- `docs/manual.pdf`
- `node_modules/` (should be ignored)

---

### Edge Case 8: Mixed Technology Stack
**Feature Request:** "Add real-time chat feature"

**Expected Behavior:**
- ✅ Detects Node.js/Express backend
- ✅ Suggests Socket.io (compatible with Express)
- ✅ References existing middleware patterns
- ✅ Warns about WebSocket infrastructure needs
- ✅ Complexity score: 10/13 (significant addition)

---

### Edge Case 9: Security-Sensitive Feature
**Feature Request:** "Add admin panel with user management"

**Expected Behavior:**
- ✅ Detects existing role-based auth (customer, vendor, admin)
- ✅ References authorize middleware
- ✅ Emphasizes security considerations:
  - CSRF protection
  - Input sanitization
  - Audit logging
- ✅ Suggests security best practices
- ✅ Complexity score: 8/13 (moderate with security focus)

---

### Edge Case 10: Database Schema Change
**Feature Request:** "Add product variants (size, color) support"

**Expected Behavior:**
- ✅ Analyzes current Product schema
- ✅ Identifies schema modification needed
- ✅ Warns about data migration requirements
- ✅ Suggests backward compatibility approach
- ✅ Complexity score: 11/13 (high - schema change)

**Migration Considerations:**
- Existing products need default variant
- Inventory tracking per variant
- Price variations per variant

---

## 🎬 Demo Video Specific Tests

### Pre-Recording Checklist Tests

#### Test 1: Application Startup
```bash
# Verify application starts cleanly
python main.py
# OR
streamlit run static/server.py
```

**Expected:**
- ✅ No errors on startup
- ✅ UI loads within 3 seconds
- ✅ Sample repository path pre-filled (optional)

---

#### Test 2: Sample Repository Loading
**Action:** Load `sample_repos/ecommerce-api`

**Expected:**
- ✅ Indexing completes in < 10 seconds
- ✅ File count displayed: ~15 files
- ✅ Success message shown
- ✅ IBM Bob audit log created

---

#### Test 3: Feature Generation Speed
**Action:** Generate spec for "Add payment processing with Stripe"

**Expected:**
- ✅ Processing indicator shown
- ✅ Generation completes in < 30 seconds
- ✅ Spec appears with proper formatting
- ✅ All sections populated (Overview, Architecture, Implementation, etc.)

---

#### Test 4: IBM Bob Export
**Action:** Click "Export IBM Bob Session Report"

**Expected:**
- ✅ File downloads immediately
- ✅ JSON format with proper structure
- ✅ Contains all audit events
- ✅ Timestamp and session ID present

---

### Visual Quality Tests

#### Test 5: UI Responsiveness
**Actions:**
- Scroll through generated spec
- Click between sections
- Resize window

**Expected:**
- ✅ Smooth scrolling
- ✅ No layout breaks
- ✅ Readable at 1080p recording resolution

---

#### Test 6: Error Display
**Action:** Trigger an error (invalid path)

**Expected:**
- ✅ Error message clearly visible
- ✅ Red/warning color scheme
- ✅ Helpful error text
- ✅ No stack traces shown to user

---

## 🔬 Technical Validation Tests

### Test 7: Architectural Weighting Verification
**Feature Request:** "Add email notifications"

**Validation:**
- ✅ Models weighted 3x (User model for email field)
- ✅ Routes weighted 2x (notification routes)
- ✅ Config files weighted 1x (email config)
- ✅ Retrieval prioritizes models first

**Check IBM Bob Audit:**
```json
{
  "operation": "retrieve_context",
  "files_retrieved": [
    "src/models/user.js",  // Should appear first
    "src/routes/...",      // Should appear second
    "src/config/..."       // Should appear last
  ]
}
```

---

### Test 8: Synonym Expansion Verification
**Feature Request:** "Add login functionality"

**Expected Synonyms Searched:**
- authentication, auth, JWT, token, session, signin, sign-in, credentials, password, OAuth, SSO

**Validation:**
- ✅ Check IBM Bob audit for search queries
- ✅ Verify multiple related files retrieved
- ✅ Confirm auth.js found despite saying "login"

---

### Test 9: Complexity Scoring Accuracy
**Test Cases:**

| Feature Request | Expected Score | Reason |
|----------------|----------------|---------|
| "Add a new field to User model" | 3 | Simple schema addition |
| "Add product search with filters" | 5 | Moderate - query logic |
| "Add payment processing" | 8 | Moderate-high - external integration |
| "Migrate from MongoDB to PostgreSQL" | 13 | Major - complete rewrite |
| "Add real-time notifications" | 10 | High - new infrastructure |

**Validation:**
- ✅ Scores match expected ranges (±1 point acceptable)
- ✅ Justification provided in spec
- ✅ Fibonacci sequence used (1,2,3,5,8,13)

---

### Test 10: Zero Hallucination Verification
**Feature Request:** "Add caching layer"

**Validation:**
- ✅ Only suggests technologies compatible with Node.js
- ✅ References actual dependencies in package.json
- ✅ Doesn't suggest Python/Django solutions
- ✅ Doesn't invent non-existent files or functions

**Red Flags to Check:**
- ❌ Suggesting SQL for MongoDB project
- ❌ Referencing files that don't exist
- ❌ Proposing incompatible frameworks
- ❌ Inventing API endpoints not in codebase

---

## 🚨 Failure Recovery Tests

### Test 11: Network Interruption
**Scenario:** Disconnect network during generation

**Expected:**
- ⚠️ Graceful timeout error
- ⚠️ "Unable to connect to Watsonx" message
- ⚠️ IBM Bob logs the failure
- ⚠️ Application remains responsive
- ⚠️ Can retry after reconnection

---

### Test 12: Watsonx API Error
**Scenario:** Simulate API error (rate limit, auth failure)

**Expected:**
- ⚠️ Clear error message to user
- ⚠️ Suggests checking API credentials
- ⚠️ IBM Bob logs the API error
- ⚠️ No partial/corrupted spec generated

---

### Test 13: Corrupted Repository
**Scenario:** Repository with syntax errors in code files

**Expected:**
- ✅ Indexing completes (best effort)
- ⚠️ Warning about unparseable files
- ✅ Generation proceeds with available context
- ✅ IBM Bob logs parsing errors

---

## 📊 Performance Benchmarks

### Benchmark 1: Small Repository (< 20 files)
- **Indexing:** < 5 seconds
- **Retrieval:** < 2 seconds
- **Generation:** < 20 seconds
- **Total:** < 30 seconds

### Benchmark 2: Medium Repository (20-50 files)
- **Indexing:** < 10 seconds
- **Retrieval:** < 5 seconds
- **Generation:** < 25 seconds
- **Total:** < 40 seconds

### Benchmark 3: Large Repository (50-100 files)
- **Indexing:** < 15 seconds
- **Retrieval:** < 8 seconds
- **Generation:** < 30 seconds
- **Total:** < 55 seconds

---

## ✅ Pre-Demo Validation Checklist

Run these tests before recording:

- [ ] **Test 1:** Application starts without errors
- [ ] **Test 2:** Sample repo loads successfully
- [ ] **Test 3:** Main demo scenario generates in < 30s
- [ ] **Test 4:** IBM Bob export works
- [ ] **Test 5:** UI is responsive and clean
- [ ] **Test 6:** Error handling works gracefully
- [ ] **Test 7:** Architectural weighting verified
- [ ] **Test 8:** Synonym expansion working
- [ ] **Test 9:** Complexity scores accurate
- [ ] **Test 10:** No hallucinations detected
- [ ] **Test 11:** Network error handled
- [ ] **Test 12:** API error handled
- [ ] **Test 13:** Corrupted files handled

---

## 🎯 Demo Day Quick Tests (5 Minutes)

Right before recording, run these quick smoke tests:

```bash
# 1. Start application
python main.py

# 2. Load sample repo
# Input: sample_repos/ecommerce-api
# Expected: Success in < 10s

# 3. Generate main demo spec
# Input: "Add payment processing with Stripe"
# Expected: Complete in < 30s

# 4. Export IBM Bob report
# Expected: File downloads successfully

# 5. Test one edge case
# Input: "Add GraphQL API"
# Expected: Warns about architectural mismatch
```

**If all 5 pass → Ready to record! 🎬**

---

## 📝 Test Results Template

```markdown
## Test Execution Report
**Date:** [Date]
**Tester:** [Name]
**Environment:** [OS, Python version]

### Primary Scenarios
- [ ] Scenario 1: Payment Integration - PASS/FAIL
- [ ] Scenario 2: Wishlist Enhancement - PASS/FAIL
- [ ] Scenario 3: Review System - PASS/FAIL

### Edge Cases
- [ ] Empty Repository - PASS/FAIL
- [ ] Invalid Path - PASS/FAIL
- [ ] Incompatible Tech - PASS/FAIL
- [ ] Vague Request - PASS/FAIL
- [ ] Already Implemented - PASS/FAIL
- [ ] Large Repository - PASS/FAIL
- [ ] Binary Files - PASS/FAIL
- [ ] Mixed Stack - PASS/FAIL
- [ ] Security Feature - PASS/FAIL
- [ ] Schema Change - PASS/FAIL

### Performance
- Indexing Time: [X] seconds
- Generation Time: [X] seconds
- Total Time: [X] seconds

### Issues Found
1. [Issue description]
2. [Issue description]

### Notes
[Any additional observations]
```

---

## 🎓 Testing Best Practices

1. **Test in order:** Primary scenarios → Edge cases → Performance
2. **Document everything:** Screenshot failures, note timings
3. **Test on clean state:** Restart application between major tests
4. **Verify IBM Bob logs:** Check audit trail after each test
5. **Practice the demo:** Run primary scenario 3-5 times
6. **Have backup plan:** Know how to handle common errors
7. **Time everything:** Ensure demo fits in 2 minutes

---

## 🚀 Ready for Demo?

**All tests passing?** ✅  
**Performance acceptable?** ✅  
**IBM Bob integration working?** ✅  
**Error handling graceful?** ✅  

**You're ready to record! Good luck! 🌟**

---

**Last Updated:** 2026-05-02  
**Version:** 1.0  
**Status:** Ready for Demo Video Recording