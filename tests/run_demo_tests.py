"""
Quick test runner for demo video preparation.
Run this script to validate all components are working before recording.
"""

import sys
import os
from pathlib import Path
import time
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def test_imports():
    """Test that all required modules can be imported."""
    print_header("Testing Module Imports")
    
    modules = [
        ("core.indexer", "CoreIndexer"),
        ("core.retriever", "RetrieverAgent"),
        ("agents.generator", "GeneratorAgent"),
        ("agents.manager", "ManagerAgent"),
        ("integrations.ibm_bob_client", "IBMBobClient"),
        ("integrations.watsonx_client", "WatsonxClient"),
    ]
    
    all_passed = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print_success(f"Imported {module_name}.{class_name}")
        except Exception as e:
            print_error(f"Failed to import {module_name}.{class_name}: {e}")
            all_passed = False
    
    return all_passed


def test_indexing():
    """Test the indexing pipeline."""
    print_header("Testing Indexing Pipeline")
    
    try:
        from core.indexer import CoreIndexer
        
        # Create test metadata
        mock_metadata = {
            "directory_map": [
                "src/models/user.js",
                "src/models/product.js",
                "src/routes/auth.js",
                "package.json"
            ],
            "tech_stack": "Node.js + Express + MongoDB",
            "database": "MongoDB",
            "file_contents": {
                "src/models/user.js": "const userSchema = new mongoose.Schema({ email: String, password: String });",
                "src/models/product.js": "const productSchema = new mongoose.Schema({ name: String, price: Number });",
                "src/routes/auth.js": "router.post('/login', async (req, res) => {});",
                "package.json": '{"dependencies": {"express": "^4.18.2", "stripe": "^14.7.0"}}'
            },
            "file_tags": {
                "src/models/user.js": ["model", "auth"],
                "src/models/product.js": ["model"],
                "src/routes/auth.js": ["route", "auth"],
                "package.json": ["config"]
            },
            "api_patterns": [
                {"method": "POST", "path": "/api/auth/login", "file": "src/routes/auth.js"}
            ],
            "dependencies": {"express": "^4.18.2", "stripe": "^14.7.0"}
        }
        
        indexer = CoreIndexer(index_path="data/index_test")
        
        start_time = time.time()
        file_count = indexer.index_repository(mock_metadata)
        duration = time.time() - start_time
        
        print_success(f"Indexed {file_count} files in {duration:.2f}s")
        
        # Verify weighting
        if "src/models/user.js" in indexer.vector_store:
            weight = indexer.vector_store["src/models/user.js"]["priority_weight"]
            if weight == 3.0:
                print_success(f"Model weighting correct: {weight}x")
            else:
                print_warning(f"Model weight is {weight}, expected 3.0")
        
        # Check if index file was created
        index_file = Path("data/index_test/repo_index.json")
        if index_file.exists():
            print_success(f"Index file created: {index_file}")
        else:
            print_error("Index file not created")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Indexing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retrieval():
    """Test the retrieval and synonym expansion."""
    print_header("Testing Retrieval & Synonym Expansion")
    
    try:
        from core.retriever import RetrieverAgent
        
        retriever = RetrieverAgent(index_path="data/index_test/repo_index.json")
        
        # Test synonym expansion
        print_info("Testing synonym expansion for 'login'...")
        expanded = retriever._expand_keywords("login")
        
        expected_synonyms = ["authentication", "jwt", "token", "auth"]
        found_synonyms = [s for s in expected_synonyms if s in expanded]
        
        if len(found_synonyms) >= 3:
            print_success(f"Synonym expansion working: {', '.join(found_synonyms[:5])}")
        else:
            print_warning(f"Only found {len(found_synonyms)} expected synonyms")
        
        # Test retrieval
        print_info("Testing retrieval for 'add payment processing'...")
        start_time = time.time()
        anchors = retriever.retrieve_relevant_anchors("add payment processing with Stripe")
        duration = time.time() - start_time
        
        print_success(f"Retrieved {len(anchors)} anchors in {duration:.2f}s")
        
        if anchors:
            print_info(f"Top result: {anchors[0]['file']} (relevance: {anchors[0]['relevance']:.2f})")
        
        # Test metadata retrieval
        metadata = retriever.get_metadata()
        if metadata:
            print_success(f"Metadata retrieved: {metadata.get('tech_stack', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print_error(f"Retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generation():
    """Test the specification generation."""
    print_header("Testing Specification Generation")
    
    try:
        from agents.generator import GeneratorAgent
        
        generator = GeneratorAgent()
        
        mock_anchors = [
            {
                "file": "src/models/order.js",
                "snippet": "paymentMethod, paymentResult, stripe integration",
                "relevance": 5.0,
                "tags": ["model"],
                "api_endpoints": [],
                "stack": "Node.js"
            },
            {
                "file": "package.json",
                "snippet": '{"dependencies": {"stripe": "^14.7.0"}}',
                "relevance": 3.0,
                "tags": ["config"],
                "api_endpoints": [],
                "stack": "Node.js"
            }
        ]
        
        mock_metadata = {
            "tech_stack": "Node.js + Express + MongoDB",
            "database": "MongoDB",
            "total_files": 15,
            "dependencies": {"stripe": "^14.7.0", "express": "^4.18.2"}
        }
        
        print_info("Generating specification (this may take 10-30 seconds)...")
        start_time = time.time()
        
        spec = generator.generate_spec(
            "Payment Integration",
            "Add payment processing with Stripe for order checkout",
            mock_anchors,
            mock_metadata
        )
        
        duration = time.time() - start_time
        
        if spec and len(spec) > 100:
            print_success(f"Generated {len(spec)} character spec in {duration:.2f}s")
            
            # Check for key sections
            sections = ["Payment", "Stripe", "order", "checkout"]
            found = [s for s in sections if s.lower() in spec.lower()]
            print_info(f"Found keywords: {', '.join(found)}")
            
            # Performance check
            if duration < 30:
                print_success(f"Generation time under 30s target ✓")
            else:
                print_warning(f"Generation took {duration:.2f}s (target: <30s)")
            
            return True
        else:
            print_error("Generated spec is too short or empty")
            return False
        
    except Exception as e:
        print_error(f"Generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end():
    """Test the complete pipeline."""
    print_header("Testing End-to-End Pipeline")
    
    try:
        from core.indexer import CoreIndexer
        from core.retriever import RetrieverAgent
        from agents.generator import GeneratorAgent
        
        # Full pipeline test
        print_info("Step 1: Indexing sample repository...")
        
        mock_metadata = {
            "directory_map": [
                "src/models/user.js",
                "src/models/product.js",
                "src/models/order.js",
                "src/routes/auth.js",
                "src/routes/products.js",
                "src/routes/orders.js",
                "src/middleware/auth.js",
                "package.json"
            ],
            "tech_stack": "Node.js + Express + MongoDB",
            "database": "MongoDB",
            "file_contents": {
                "src/models/order.js": "paymentMethod paymentResult stripe totalAmount",
                "package.json": '{"dependencies": {"stripe": "^14.7.0", "express": "^4.18.2"}}'
            },
            "file_tags": {
                "src/models/user.js": ["model", "auth"],
                "src/models/product.js": ["model"],
                "src/models/order.js": ["model"],
                "src/routes/auth.js": ["route", "auth"],
                "src/routes/products.js": ["route"],
                "src/routes/orders.js": ["route"],
                "src/middleware/auth.js": ["middleware", "auth"],
                "package.json": ["config"]
            },
            "api_patterns": [
                {"method": "POST", "path": "/api/orders", "file": "src/routes/orders.js"}
            ],
            "dependencies": {"stripe": "^14.7.0", "express": "^4.18.2"}
        }
        
        start_total = time.time()
        
        indexer = CoreIndexer(index_path="data/index_test")
        file_count = indexer.index_repository(mock_metadata)
        print_success(f"Indexed {file_count} files")
        
        print_info("Step 2: Retrieving relevant context...")
        retriever = RetrieverAgent(index_path="data/index_test/repo_index.json")
        anchors = retriever.retrieve_relevant_anchors("Add payment processing with Stripe")
        print_success(f"Retrieved {len(anchors)} relevant files")
        
        print_info("Step 3: Generating specification...")
        generator = GeneratorAgent()
        spec = generator.generate_spec(
            "Payment Integration",
            "Add payment processing with Stripe",
            anchors,
            retriever.get_metadata()
        )
        
        total_duration = time.time() - start_total
        
        if spec and len(spec) > 100:
            print_success(f"Complete pipeline executed in {total_duration:.2f}s")
            
            if total_duration < 45:
                print_success("✓ Total time under 45s target for demo")
            else:
                print_warning(f"Total time {total_duration:.2f}s exceeds 45s target")
            
            return True
        else:
            print_error("Pipeline completed but spec is invalid")
            return False
        
    except Exception as e:
        print_error(f"End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge case handling."""
    print_header("Testing Edge Cases")
    
    try:
        from core.indexer import CoreIndexer
        from core.retriever import RetrieverAgent
        
        # Test 1: Empty repository
        print_info("Test 1: Empty repository...")
        empty_metadata = {
            "directory_map": [],
            "tech_stack": "Unknown",
            "database": "Unknown",
            "file_contents": {},
            "file_tags": {},
            "api_patterns": [],
            "dependencies": {}
        }
        
        indexer = CoreIndexer(index_path="data/index_test_empty")
        file_count = indexer.index_repository(empty_metadata)
        
        if file_count == 0:
            print_success("Empty repository handled correctly")
        else:
            print_warning(f"Expected 0 files, got {file_count}")
        
        # Test 2: No matching files
        print_info("Test 2: No matching files for query...")
        retriever = RetrieverAgent(index_path="data/index_test/repo_index.json")
        anchors = retriever.retrieve_relevant_anchors("add blockchain quantum AI")
        
        if len(anchors) == 0 or (len(anchors) > 0 and anchors[0]['relevance'] < 1.0):
            print_success("No false positives for unrelated query")
        else:
            print_warning(f"Found {len(anchors)} matches for unrelated query")
        
        return True
        
    except Exception as e:
        print_error(f"Edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sample_repo_integration():
    """Test with actual sample repository if available."""
    print_header("Testing Sample Repository Integration")
    
    sample_repo_path = Path("sample_repos/ecommerce-api")
    
    if not sample_repo_path.exists():
        print_warning("Sample repository not found, skipping this test")
        return True
    
    try:
        from integrations.ibm_bob_client import IBMBobClient
        
        print_info(f"Scanning sample repository: {sample_repo_path}")
        
        bob_client = IBMBobClient(repo_path=str(sample_repo_path))
        metadata = bob_client.get_repository_context()
        
        print_success(f"Tech Stack: {metadata.get('tech_stack', 'Unknown')}")
        print_success(f"Database: {metadata.get('database', 'Unknown')}")
        print_success(f"Files Found: {len(metadata.get('directory_map', []))}")
        
        if metadata.get('dependencies'):
            deps = list(metadata['dependencies'].keys())[:5]
            print_info(f"Dependencies: {', '.join(deps)}")
        
        return True
        
    except Exception as e:
        print_error(f"Sample repo test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{'ArcSync Demo Test Suite'.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = {}
    
    # Run all tests
    results['imports'] = test_imports()
    results['indexing'] = test_indexing()
    results['retrieval'] = test_retrieval()
    results['generation'] = test_generation()
    results['end_to_end'] = test_end_to_end()
    results['edge_cases'] = test_edge_cases()
    results['sample_repo'] = test_sample_repo_integration()
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    
    if passed == total:
        print(f"{GREEN}✓ All tests passed! ({passed}/{total}){RESET}")
        print(f"{GREEN}✓ Ready for demo video recording!{RESET}")
        return 0
    else:
        print(f"{YELLOW}⚠ {passed}/{total} tests passed{RESET}")
        print(f"{YELLOW}⚠ Fix failing tests before recording demo{RESET}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

# Made with Bob
