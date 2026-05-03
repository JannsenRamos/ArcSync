import warnings
warnings.filterwarnings('ignore')

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print(f"Python: {sys.version}")

# Test 1: Core imports
try:
    from integrations.ibm_bob_client import IBMBobClient
    from integrations.watsonx_client import WatsonxClient, get_watsonx_client
    from core.indexer import CoreIndexer
    from core.retriever import RetrieverAgent
    from agents.generator import GeneratorAgent
    from agents.manager import ManagerAgent
    from agents.context_agent import ContextAgent
    print("OK: All ArcSync modules imported")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Initialize with sample repo
try:
    import os
    sample_repo = os.path.join(os.path.dirname(__file__), "sample_repos", "ecommerce-api")
    print(f"\nInitializing ManagerAgent for: {sample_repo}")
    manager = ManagerAgent(repo_path=sample_repo)
    print("OK: ManagerAgent initialized")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Generate a spec
try:
    print("\nGenerating spec for 'Add Stripe payment integration'...")
    spec = manager.orchestrate_spec_request(
        "Stripe Payment Integration",
        "Add Stripe payment integration with checkout, webhooks, and subscription support"
    )
    print(f"OK: Spec generated ({len(spec)} chars)")
    print("\n--- First 500 chars ---")
    print(spec[:500])
    print("--- End ---")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll tests passed!")
