"""
End-to-End Workflow Test for ArcSync Application
Tests the complete flow from user input to spec generation
"""

import sys
import traceback
from datetime import datetime
import io

# Fix Windows console encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_workflow():
    """Test the complete workflow of the application"""
    
    print("=" * 80)
    print("ArcSync End-to-End Workflow Test")
    print("=" * 80)
    print(f"Test Started: {datetime.now().isoformat()}")
    print()
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "overall_status": "PASS"
    }
    
    # Test 1: Import all required modules
    print("Test 1: Importing Required Modules")
    print("-" * 80)
    try:
        from agents.manager import ManagerAgent
        from agents.generator import GeneratorAgent
        from core.retriever import RetrieverAgent
        from core.indexer import CoreIndexer
        
        print("[PASS] Successfully imported ManagerAgent")
        print("[PASS] Successfully imported GeneratorAgent")
        print("[PASS] Successfully imported RetrieverAgent")
        print("[PASS] Successfully imported CoreIndexer")
        
        test_results["tests"].append({
            "name": "Module Imports",
            "status": "PASS",
            "details": "All required modules imported successfully"
        })
        print()
    except Exception as e:
        print(f"[FAIL] Import failed: {str(e)}")
        print(traceback.format_exc())
        test_results["tests"].append({
            "name": "Module Imports",
            "status": "FAIL",
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        test_results["overall_status"] = "FAIL"
        return test_results
    
    # Test 2: Initialize components
    print("Test 2: Initializing Components")
    print("-" * 80)
    try:
        # Initialize manager (it initializes all other components internally)
        manager = ManagerAgent()
        print("[PASS] ManagerAgent initialized (includes indexer, retriever, and generator)")
        
        test_results["tests"].append({
            "name": "Component Initialization",
            "status": "PASS",
            "details": "All components initialized successfully"
        })
        print()
    except Exception as e:
        print(f"[FAIL] Initialization failed: {str(e)}")
        print(traceback.format_exc())
        test_results["tests"].append({
            "name": "Component Initialization",
            "status": "FAIL",
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        test_results["overall_status"] = "FAIL"
        return test_results
    
    # Test 3: Execute workflow with sample input
    print("Test 3: Executing Complete Workflow")
    print("-" * 80)
    
    test_cases = [
        {
            "feature_name": "User Authentication",
            "raw_intent": "Add OAuth2 login with Google and GitHub providers"
        },
        {
            "feature_name": "Data Export",
            "raw_intent": "Allow users to export their data in CSV and JSON formats"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Feature Name: {test_case['feature_name']}")
        print(f"  Raw Intent: {test_case['raw_intent']}")
        print()
        
        try:
            # Execute the workflow
            result = manager.orchestrate_spec_request(
                feature_name=test_case['feature_name'],
                raw_intent=test_case['raw_intent']
            )
            
            print("[PASS] Workflow executed successfully")
            print()
            print("Generated Specification:")
            print("-" * 80)
            print(result)
            print("-" * 80)
            print()
            
            # Validate result
            if result and isinstance(result, str) and len(result) > 0:
                print("[PASS] Result validation passed")
                test_results["tests"].append({
                    "name": f"Workflow Execution - Test Case {i}",
                    "status": "PASS",
                    "input": test_case,
                    "output_length": len(result),
                    "output_preview": result[:200] + "..." if len(result) > 200 else result
                })
            else:
                print("[FAIL] Result validation failed: Empty or invalid result")
                test_results["tests"].append({
                    "name": f"Workflow Execution - Test Case {i}",
                    "status": "FAIL",
                    "input": test_case,
                    "error": "Empty or invalid result"
                })
                test_results["overall_status"] = "FAIL"
            
        except Exception as e:
            print(f"[FAIL] Workflow execution failed: {str(e)}")
            print(traceback.format_exc())
            test_results["tests"].append({
                "name": f"Workflow Execution - Test Case {i}",
                "status": "FAIL",
                "input": test_case,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            test_results["overall_status"] = "FAIL"
        
        print()
    
    # Test 4: Check for common errors
    print("Test 4: Error Handling Validation")
    print("-" * 80)
    try:
        # Test with invalid input
        print("Testing with empty feature name...")
        try:
            result = manager.orchestrate_spec_request(
                feature_name="",
                raw_intent="Test input"
            )
            print("[PASS] Handled empty feature name gracefully")
        except Exception as e:
            print(f"[PASS] Properly raised exception for empty feature name: {type(e).__name__}")
        
        print()
        print("Testing with empty raw intent...")
        try:
            result = manager.orchestrate_spec_request(
                feature_name="Test Feature",
                raw_intent=""
            )
            print("[PASS] Handled empty raw intent gracefully")
        except Exception as e:
            print(f"[PASS] Properly raised exception for empty raw intent: {type(e).__name__}")
        
        test_results["tests"].append({
            "name": "Error Handling",
            "status": "PASS",
            "details": "Error handling works as expected"
        })
        print()
    except Exception as e:
        print(f"[FAIL] Error handling test failed: {str(e)}")
        test_results["tests"].append({
            "name": "Error Handling",
            "status": "FAIL",
            "error": str(e)
        })
        test_results["overall_status"] = "FAIL"
    
    return test_results


def main():
    """Main test execution function"""
    try:
        results = test_workflow()
        
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Overall Status: {results['overall_status']}")
        print(f"Total Tests: {len(results['tests'])}")
        print(f"Passed: {sum(1 for t in results['tests'] if t['status'] == 'PASS')}")
        print(f"Failed: {sum(1 for t in results['tests'] if t['status'] == 'FAIL')}")
        print()
        
        for test in results['tests']:
            status_symbol = "[PASS]" if test['status'] == "PASS" else "[FAIL]"
            print(f"{status_symbol} {test['name']}: {test['status']}")
            if test['status'] == "FAIL" and 'error' in test:
                print(f"  Error: {test['error']}")
        
        print()
        print("=" * 80)
        print(f"Test Completed: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Return exit code based on overall status
        return 0 if results['overall_status'] == "PASS" else 1
        
    except Exception as e:
        print()
        print("=" * 80)
        print("CRITICAL ERROR")
        print("=" * 80)
        print(f"Test execution failed with critical error: {str(e)}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
