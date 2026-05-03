# Testing ArcSync with Real Repositories

This guide explains how to test ArcSync with your own repositories instead of just the sample repos.

## Quick Start

### Option 1: Use the `test_repos` Directory (Recommended)

1. **Create the test_repos directory:**
```bash
mkdir test_repos
cd test_repos
```

2. **Clone or copy your repositories:**
```bash
# Clone a repo
git clone https://github.com/your-username/your-repo.git

# Or copy an existing local repo
cp -r /path/to/your/project ./my-project
```

3. **Restart the server:**
```bash
cd ..
python static/server.py
```

The web app will automatically detect repos in `test_repos/` and add them to the repository selector!

### Option 2: Modify SAMPLE_REPOS Directly

Edit `static/server.py` and add your repo path:

```python
repos.append({
    "name": "My Custom Project",
    "path": "/absolute/path/to/your/project",
    "description": "Description of your project"
})
```

## Recommended Test Repositories

### Good Candidates for Testing:
- **Small to Medium Projects** (100-1000 files)
- **Well-structured codebases** with clear patterns
- **Projects you're familiar with** (easier to verify accuracy)

### Repository Types That Work Well:
1. **REST APIs** (Express, FastAPI, Django, Flask)
2. **Web Apps** (React, Vue, Angular with backend)
3. **Microservices** (Node.js, Python, Go)
4. **Mobile Backends** (any language)

### What to Avoid:
- ❌ Monorepos with 10,000+ files (too slow)
- ❌ Repos with mostly binary files
- ❌ Empty or skeleton projects (not enough context)

## Example Test Scenarios

### Scenario 1: E-Commerce Platform
```
Repository: Node.js/Express + MongoDB e-commerce API
Test Feature: "Add wishlist functionality where users can save products"
Expected: Should detect existing user/product models, suggest new wishlist routes
```

### Scenario 2: SaaS Dashboard
```
Repository: React + Python/FastAPI dashboard
Test Feature: "Add real-time notifications using WebSockets"
Expected: Should identify auth patterns, suggest WebSocket integration points
```

### Scenario 3: Mobile Backend
```
Repository: Django REST API for mobile app
Test Feature: "Add push notification support via Firebase"
Expected: Should detect existing notification patterns, suggest Firebase integration
```

## Directory Structure Example

```
ArcSync/
├── sample_repos/          # Pre-included samples
│   └── ecommerce-api/
├── test_repos/            # Your test repositories (auto-detected)
│   ├── my-saas-backend/
│   ├── mobile-api/
│   └── react-dashboard/
├── static/
│   └── server.py
└── ...
```

## Testing Workflow

1. **Add Repository**
   - Place repo in `test_repos/` directory
   - Restart server: `python static/server.py`

2. **Verify Detection**
   - Open http://localhost:8000
   - Check repository selector shows your repo
   - Verify tech stack/database badges are correct

3. **Test Feature Generation**
   - Enter a realistic feature request
   - Click "Process Requirements"
   - Verify:
     - ✓ Correct files are matched (anchors)
     - ✓ Complexity score makes sense
     - ✓ Proposed changes reference actual files
     - ✓ API design follows existing patterns

4. **Validate Output**
   - Check if suggested changes are feasible
   - Verify file paths exist in your repo
   - Confirm tech stack recommendations match

## Common Issues & Solutions

### Issue: Repository Not Detected
**Solution:** 
- Ensure directory is directly under `test_repos/`
- Check directory isn't hidden (no `.` prefix)
- Restart the server

### Issue: Wrong Tech Stack Detected
**Solution:**
- Check if repo has clear indicators (package.json, requirements.txt, etc.)
- Add a README with tech stack info
- The indexer looks for common patterns

### Issue: No Files Matched
**Solution:**
- Ensure repo has actual code files (not just README)
- Check if feature request is too vague
- Try more specific keywords related to your codebase

### Issue: Slow Performance
**Solution:**
- Limit repo size to < 1000 files
- Exclude node_modules, venv, build directories
- Add `.gitignore` patterns

## Advanced: Testing with Private Repos

If testing with private/sensitive code:

1. **Create a sanitized copy:**
```bash
# Copy repo structure without sensitive data
rsync -av --exclude='*.env' --exclude='secrets/' \
  /path/to/private-repo ./test_repos/sanitized-copy
```

2. **Remove sensitive files:**
```bash
cd test_repos/sanitized-copy
rm -rf .env config/secrets.json
```

3. **Test with sanitized version**

## Performance Tips

- **First run is slow** (indexing) - subsequent runs are fast
- **Smaller repos** = faster analysis
- **Clear patterns** = better results
- **Good naming** = more accurate matching

## Example Test Commands

```bash
# Test with a real GitHub repo
cd test_repos
git clone https://github.com/gothinkster/realworld.git
cd ..
python static/server.py

# Test with your local project
cp -r ~/projects/my-app ./test_repos/
python static/server.py
```

## Validation Checklist

After testing with a real repo, verify:

- [ ] Repository appears in selector
- [ ] Tech stack badge is accurate
- [ ] File count is reasonable
- [ ] Feature generation completes
- [ ] Matched files are relevant
- [ ] Complexity score makes sense
- [ ] Proposed changes reference real files
- [ ] API suggestions follow existing patterns
- [ ] Gherkin scenarios are realistic

## Need Help?

If you encounter issues:
1. Check server logs for errors
2. Verify repo structure is standard
3. Try with a simpler/smaller repo first
4. Check that dependencies are installed

---

**Pro Tip:** Start with repos you know well - it's easier to validate if the AI's suggestions make sense!