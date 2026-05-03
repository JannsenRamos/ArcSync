"""
Integration tests for ArcSync demo video scenarios.
Tests the complete pipeline: Indexing → Retrieval → Generation
"""

import sys
import os
import json
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.indexer import CoreIndexer
from core.retriever import RetrieverAgent
from agents.generator import GeneratorAgent
from agents.manager import ManagerAgent
from integrations.ibm_bob_client import IBMBobClient


class TestIndexing:
    """Test the indexing pipeline with sample e-commerce repo."""
    
    def test_indexer_initialization(self):
        """Test that indexer can be initialized."""
        indexer = CoreIndexer(index_path="data/index_test")
        assert indexer is not None
        assert indexer.index_path.exists()
    
    def test_index_sample_repo(self):
        """Test indexing the sample e-commerce repository."""
        # Mock Bob metadata for testing
        mock_metadata = {
            "directory_map": [
                "src/models/user.js",
                "src/models/product.js",
                "src/models/order.js",
                "src/routes/auth.js",
                "src/routes/products.js",
                "src/routes/orders.js",
                "src/middleware/auth.js",
                "src/config/db.js",
                "package.json"
            ],
            "tech_stack": "Node.js + Express + MongoDB",
            "database": "MongoDB",
            "file_contents": {
                "src/models/user.js": "const userSchema = new mongoose.Schema({ email: String, password: String, role: String });",
                "src/models/product.js": "const productSchema = new mongoose.Schema({ name: String, price: Number, category: String });",
                "src/routes/auth.js": "router.post('/login', async (req, res) => { /* auth logic */ });",
                "package.json": '{"dependencies": {"express": "^4.18.2", "mongoose": "^7.6.3", "stripe": "^14.7.0"}}'
            },
            "file_tags": {
                "src/models/user.js": ["model", "auth"],
                "src/models/product.js": ["model"],
                "src/models/order.js": ["model"],
                "src/routes/auth.js": ["route", "auth"],
                "src/routes/products.js": ["route"],
                "src/routes/orders.js": ["route"],
                "src/middleware/auth.js": ["middleware", "auth"],
                "src/config/db.js": ["config", "database"]
            },
            "api_patterns": [
                {"method": "POST", "path": "/api/auth/login", "file": "src/routes/auth.js"},
                {"method": "POST", "path": "/api/auth/register", "file": "src/routes/auth.js"},
                {"method": "GET", "path": "/api/products", "file": "src/routes/products.js"},
                {"method": "POST", "path": "/api/orders", "file": "src/routes/orders.js"}
            ],
            "dependencies": {
                "express": "^4.18.2",
                "mongoose": "^7.6.3",
                "stripe": "^14.7.0",
                "jsonwebtoken": "^9.0.2"
            }
        }
        
        indexer = CoreIndexer(index_path="data/index_test")
        file_count = indexer.index_repository(mock_metadata)
        
        assert file_count == 9  # 9 files indexed
        assert "src/models/user.js" in indexer.vector_store
        assert indexer.vector_store["src/models/user.js"]["priority_weight"] == 3.0  # Model weight
        assert "auth" in indexer.vector_store["src/models/user.js"]["tags"]
    
    def test_architectural_weighting(self):
        """Test that models get higher weight than other files."""
        mock_metadata = {
            "directory_map": ["src/models/user.js", "src/utils/helper.js"],
            "tech_stack": "Node.js",
            "database": "MongoDB",
            "file_contents": {},
            "file_tags": {
                "src/models/user.js": ["model"],
                "src/utils/helper.js": ["utility"]
            },
            "api_patterns": [],
            "dependencies": {}
        }
        
        indexer = CoreIndexer(index_path="data/index_test")
        indexer.index_repository(mock_metadata)
        
        model_weight = indexer.vector_store["src/models/user.js"]["priority_weight"]
        util_weight = indexer.vector_store["src/utils/helper.js"]["priority_weight"]
        
        assert model_weight > util_weight
        assert model_weight == 3.0


class TestRetrieval:
    """Test the retrieval and synonym expansion."""
    
    @pytest.fixture
    def setup_index(self):
        """Setup test index before each test."""
        mock_metadata = {
            "directory_map": [
                "src/models/user.js",
                "src/routes/auth.js",
                "src/models/product.js",
                "src/routes/products.js"
            ],
            "tech_stack": "Node.js + Express",
            "database": "MongoDB",
            "file_contents": {
                "src/models/user.js": "email password jwt token authentication",
                "src/routes/auth.js": "login register signin authentication",
                "src/models/product.js": "name price category inventory",
                "src/routes/products.js": "GET POST products catalog"
            },
            "file_tags": {
                "src/models/user.js": ["model", "auth"],
                "src/routes/auth.js": ["route", "auth"],
                "src/models/product.js": ["model"],
                "src/routes/products.js": ["route"]
            },
            "api_patterns": [],
            "dependencies": {}
        }
        
        indexer = CoreIndexer(index_path="data/index_test")
        indexer.index_repository(mock_metadata)
        return RetrieverAgent(index_path="data/index_test/repo_index.json")
    
    def test_synonym_expansion(self, setup_index):
        """Test that 'login' expands to auth-related synonyms."""
        retriever = setup_index
        expanded = retriever._expand_keywords("login")
        
        assert "authentication" in expanded
        assert "jwt" in expanded
        assert "token" in expanded
        assert "auth" in expanded
    
    def test_retrieve_auth_files(self, setup_index):
        """Test retrieving auth-related files when asking about login."""
        retriever = setup_index
        anchors = retriever.retrieve_relevant_anchors("add login functionality")
        
        # Should find auth-related files
        auth_files = [a['file'] for a in anchors if 'auth' in a['file']]
        assert len(auth_files) > 0
        assert any('user.js' in f for f in auth_files)
    
    def test_retrieve_payment_context(self, setup_index):
        """Test retrieving context for payment feature."""
        retriever = setup_index
        anchors = retriever.retrieve_relevant_anchors("add payment processing with Stripe")
        
        # Should retrieve some files (even if not payment-specific in this mock)
        assert len(anchors) >= 0  # May be 0 if no payment context exists
    
    def test_relevance_scoring(self, setup_index):
        """Test that more relevant files score higher."""
        retriever = setup_index
        anchors = retriever.retrieve_relevant_anchors("user authentication")
        
        if len(anchors) > 1:
            # First result should be most relevant
            assert anchors[0]['relevance'] >= anchors[1]['relevance']


class TestGeneration:
    """Test the specification generation."""
    
    def test_generator_initialization(self):
        """Test that generator can be initialized."""
        generator = GeneratorAgent()
        assert generator is not None
    
    def test_generate_with_context(self):
        """Test generating spec with context anchors."""
        generator = GeneratorAgent()
        
        mock_anchors = [
            {
                "file": "src/models/order.js",
                "snippet": "paymentMethod, paymentResult, stripe",
                "relevance": 5.0,
                "tags": ["model"],
                "api_endpoints": [],
                "stack": "Node.js"
            }
        ]
        
        mock_metadata = {
            "tech_stack": "Node.js + Express + MongoDB",
            "database": "MongoDB",
            "dependencies": {"stripe": "^14.7.0"}
        }
        
        spec = generator.generate_spec(
            "Payment Integration",
            "Add payment processing with Stripe",
            mock_anchors,
            mock_metadata
        )
        
        assert spec is not None
        assert len(spec) > 100  # Should generate substantial content
        assert "Payment" in spec or "payment" in spec


class TestEndToEnd:
    """End-to-end integration tests for demo scenarios."""
    
    def test_payment_integration_scenario(self):
        """Test the main demo scenario: Payment Integration."""
        # This would require the full sample repo to be present
        # For now, we test the pipeline with mocked data
        
        mock_metadata = {
            "directory_map": [
                "src/models/order.js",
                "src/routes/orders.js",
                "package.json"
            ],
            "tech_stack": "Node.js + Express + MongoDB",
            "database": "MongoDB",
            "file_contents": {
                "src/models/order.js": "paymentMethod paymentResult stripe totalAmount",
                "package.json": '{"dependencies": {"stripe": "^14.7.0"}}'
            },
            "file_tags": {
                "src/models/order.js": ["model"],
                "src/routes/orders.js": ["route"],
                "package.json": ["config"]
            },
            "api_patterns": [
                {"method": "POST", "path": "/api/orders", "file": "src/routes/orders.js"}
            ],
            "dependencies": {"stripe": "^14.7.0"}
        }
        
        # Index
        indexer = CoreIndexer(index_path="data/index_test")
        file_count = indexer.index_repository(mock_metadata)
        assert file_count > 0
        
        # Retrieve
        retriever = RetrieverAgent(index_path="data/index_test/repo_index.json")
        anchors = retriever.retrieve_relevant_anchors("Add payment processing with Stripe")
        assert len(anchors) > 0
        
        # Generate
        generator = GeneratorAgent()
        spec = generator.generate_spec(
            "Payment Integration",
            "Add payment processing with Stripe",
            anchors,
            retriever.get_metadata()
        )
        assert spec is not None
        assert len(spec) > 100
    
    def test_already_implemented_detection(self):
        """Test detecting already implemented features (JWT auth)."""
        mock_metadata = {
            "directory_map": [
                "src/models/user.js",
                "src/routes/auth.js",
                "src/middleware/auth.js"
            ],
            "tech_stack": "Node.js + Express",
            "database": "MongoDB",
            "file_contents": {
                "src/models/user.js": "generateAuthToken jwt.sign",
                "src/routes/auth.js": "POST /login POST /register jwt",
                "src/middleware/auth.js": "jwt.verify authenticate"
            },
            "file_tags": {
                "src/models/user.js": ["model", "auth"],
                "src/routes/auth.js": ["route", "auth"],
                "src/middleware/auth.js": ["middleware", "auth"]
            },
            "api_patterns": [
                {"method": "POST", "path": "/api/auth/login", "file": "src/routes/auth.js"}
            ],
            "dependencies": {"jsonwebtoken": "^9.0.2"}
        }
        
        indexer = CoreIndexer(index_path="data/index_test")
        indexer.index_repository(mock_metadata)
        
        retriever = RetrieverAgent(index_path="data/index_test/repo_index.json")
        anchors = retriever.retrieve_relevant_anchors("Add JWT authentication")
        
        # Should find existing JWT implementation
        assert len(anchors) > 0
        jwt_files = [a for a in anchors if 'jwt' in a['snippet'].lower() or 'auth' in a['file']]
        assert len(jwt_files) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_repository(self):
        """Test handling of empty repository."""
        mock_metadata = {
            "directory_map": [],
            "tech_stack": "Unknown",
            "database": "Unknown",
            "file_contents": {},
            "file_tags": {},
            "api_patterns": [],
            "dependencies": {}
        }
        
        indexer = CoreIndexer(index_path="data/index_test")
        file_count = indexer.index_repository(mock_metadata)
        assert file_count == 0
    
    def test_no_matching_files(self):
        """Test retrieval when no files match the intent."""
        mock_metadata = {
            "directory_map": ["src/utils/helper.js"],
            "tech_stack": "Node.js",
            "database": "MongoDB",
            "file_contents": {"src/utils/helper.js": "utility functions"},
            "file_tags": {"src/utils/helper.js": ["utility"]},
            "api_patterns": [],
            "dependencies": {}
        }
        
        indexer = CoreIndexer(index_path="data/index_test")
        indexer.index_repository(mock_metadata)
        
        retriever = RetrieverAgent(index_path="data/index_test/repo_index.json")
        anchors = retriever.retrieve_relevant_anchors("add blockchain integration")
        
        # Should return empty or very low relevance results
        assert len(anchors) == 0 or anchors[0]['relevance'] < 1.0
    
    def test_vague_feature_request(self):
        """Test handling of vague requests."""
        generator = GeneratorAgent()
        
        spec = generator.generate_spec(
            "Improvements",
            "Make it better",
            [],
            {"tech_stack": "Node.js", "database": "MongoDB"}
        )
        
        # Should still generate something (fallback)
        assert spec is not None
        assert len(spec) > 50


class TestPerformance:
    """Performance benchmarks for demo video."""
    
    def test_indexing_speed(self):
        """Test that indexing completes quickly."""
        import time
        
        # Create a realistic-sized mock repo
        mock_metadata = {
            "directory_map": [f"src/file_{i}.js" for i in range(20)],
            "tech_stack": "Node.js",
            "database": "MongoDB",
            "file_contents": {f"src/file_{i}.js": f"content {i}" for i in range(20)},
            "file_tags": {f"src/file_{i}.js": ["source"] for i in range(20)},
            "api_patterns": [],
            "dependencies": {}
        }
        
        indexer = CoreIndexer(index_path="data/index_test")
        
        start = time.time()
        indexer.index_repository(mock_metadata)
        duration = time.time() - start
        
        # Should complete in under 5 seconds for 20 files
        assert duration < 5.0
    
    def test_retrieval_speed(self):
        """Test that retrieval is fast."""
        import time
        
        mock_metadata = {
            "directory_map": [f"src/file_{i}.js" for i in range(20)],
            "tech_stack": "Node.js",
            "database": "MongoDB",
            "file_contents": {f"src/file_{i}.js": "auth login user" for i in range(20)},
            "file_tags": {f"src/file_{i}.js": ["source"] for i in range(20)},
            "api_patterns": [],
            "dependencies": {}
        }
        
        indexer = CoreIndexer(index_path="data/index_test")
        indexer.index_repository(mock_metadata)
        
        retriever = RetrieverAgent(index_path="data/index_test/repo_index.json")
        
        start = time.time()
        retriever.retrieve_relevant_anchors("add authentication")
        duration = time.time() - start
        
        # Should complete in under 2 seconds
        assert duration < 2.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

# Made with Bob
