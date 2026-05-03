import warnings
warnings.filterwarnings('ignore')

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from integrations.watsonx_client import get_watsonx_client

client = get_watsonx_client()
print(f"API Key: {client.api_key[:10]}...")
print(f"Project ID: {client.project_id}")
print(f"URL: {client.url}")

print("\nTesting Watsonx API connection...")
result = client.generate("Hello, say 'IBM Bob is ready!' in one sentence.", max_tokens=50)
print(f"\nResponse: {result[:300]}")
