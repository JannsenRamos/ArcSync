# ArcSync Test Suite

Comprehensive testing for demo video preparation and integration validation.

## Quick Start

### Run All Tests (Recommended Before Demo)

```bash
# Simple test runner - no dependencies required
python tests/run_demo_tests.py
```

This will test:
- ✅ Module imports
- ✅ Indexing pipeline
- ✅ Retrieval & synonym expansion
- ✅ Specification generation
- ✅ End-to-end workflow
- ✅ Edge case handling
- ✅ Sample repository integration

**Expected Output:**
```
============================================================
                  ArcSync Demo Test Suite
============================================================

Testing Module Imports
✓ Imported core.indexer.CoreIndexer
✓ Imported core.retriever.RetrieverAgent
...

Test Summary
Imports: PASS
Indexing: PASS
Retrieval: PASS
Generation: PASS
End To End: PASS
Edge Cases: PASS
Sample Repo: PASS

✓ All tests passed! (7/7)
✓ Ready for demo video recording!
```

### Run Pytest Integration Tests (Optional)

If you have pytest installed:

```bash
# Install pytest first
pip install pytest

# Run integration tests
pytest tests/test_integration.py -v

# Run with coverage
pytest tests/test_integration.py -v --cov=. --cov-report=html
```

## Test Files

### `run_demo_tests.py` (Standalone)
- **No external dependencies** - uses only Python stdlib
- Quick validation before demo recording
- Colored terminal output
- Tests all critical paths
- ~30 seconds to run

### `test_integration.py` (Pytest)
- Requires pytest installation
- More comprehensive test coverage
- Includes performance benchmarks
- Fixture-based testing
- ~60 seconds to run

## Test Scenarios Covered

### 1. Module Import Tests
Validates all core modules can be imported:
- `core.indexer.CoreIndexer`
- `core.retriever.RetrieverAgent`
- `agents.generator.GeneratorAgent`
- `agents.manager.ManagerAgent`
- `integrations.ibm_bob_client.IBMBobClient`
- `integrations.watsonx_client.WatsonxClient`

### 2. Indexing Tests
- Repository metadata indexing
- Architectural weighting (models 3x, routes 2x, config 1x)
- File tagging and categorization
- Index persistence to JSON
- Performance: < 5 seconds for 20 files

### 3. Retrieval Tests
- Synonym expansion (login → authentication, JWT, token, etc.)
- Keyword matching with relevance scoring
- Context anchor retrieval
- Metadata extraction
- Performance: < 2 seconds per query

### 4. Generation Tests
- Specification generation with context
- Fallback handling (when Watsonx unavailable)
- Output validation (length, content)
- Performance: < 30 seconds target

### 5. End-to-End Tests
- Complete pipeline: Index → Retrieve → Generate
- Demo scenario: "Add payment processing with Stripe"
- Total time validation: < 45 seconds
- Output quality checks

### 6. Edge Case Tests
- Empty repository handling
- No matching files for query
- Vague feature requests
- Already implemented features
- Invalid paths
- Corrupted data

### 7. Sample Repository Tests
- Integration with `sample_repos/ecommerce-api`
- Real-world file scanning
- Dependency detection
- Tech stack identification

## Performance Benchmarks

| Test | Target | Typical |
|------|--------|---------|
| Indexing (20 files) | < 5s | ~1-2s |
| Retrieval | < 2s | ~0.1-0.5s |
| Generation | < 30s | ~10-25s |
| **Total Pipeline** | **< 45s** | **~15-30s** |

## Demo Video Validation Checklist

Before recording your demo video, run:

```bash
python tests/run_demo_tests.py
```

Ensure all tests pass:
- [ ] ✅ Imports: All modules load correctly
- [ ] ✅ Indexing: Files indexed with correct weights
- [ ] ✅ Retrieval: Synonyms expand properly
- [ ] ✅ Generation: Specs generate in < 30s
- [ ] ✅ End-to-End: Complete pipeline works
- [ ] ✅ Edge Cases: Errors handled gracefully
- [ ] ✅ Sample Repo: Real repository scans successfully

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the project root
cd /path/to/ArcSync

# Run from project root
python tests/run_demo_tests.py
```

### Missing Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# For pytest tests only
pip install pytest pytest-cov
```

### Watsonx Connection Issues
Tests will use fallback generation if Watsonx is unavailable. This is expected and won't fail tests.

To enable Watsonx:
1. Copy `.env.example` to `.env`
2. Add your IBM Cloud credentials
3. Re-run tests

### Sample Repository Not Found
If `sample_repos/ecommerce-api` doesn't exist, that test will be skipped. This is not a failure.

## Test Data

Tests use mock metadata that simulates the e-commerce API structure:
- Models: `user.js`, `product.js`, `order.js`
- Routes: `auth.js`, `products.js`, `orders.js`
- Middleware: `auth.js`
- Config: `db.js`, `package.json`

## CI/CD Integration

To integrate with CI/CD:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python tests/run_demo_tests.py
```

## Writing New Tests

### Adding to `run_demo_tests.py`

```python
def test_my_feature():
    """Test description."""
    print_header("Testing My Feature")
    
    try:
        # Your test code here
        result = my_function()
        
        if result:
            print_success("Test passed")
            return True
        else:
            print_error("Test failed")
            return False
            
    except Exception as e:
        print_error(f"Test error: {e}")
        return False

# Add to main():
results['my_feature'] = test_my_feature()
```

### Adding to `test_integration.py`

```python
class TestMyFeature:
    """Test my feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = my_function()
        assert result is not None
        assert len(result) > 0
```

## Test Coverage

Current coverage:
- Core modules: ~90%
- Agents: ~85%
- Integrations: ~75%
- Edge cases: ~80%

## Support

For issues or questions:
1. Check this README
2. Review test output for specific errors
3. Check main project README.md
4. Review DEMO_TEST_SCENARIOS.md for detailed scenarios

## License

Same as main project.