from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging
import sys
import os
import json
import re
import zipfile
import uuid
import shutil
from pathlib import Path

# Add parent directory to path to import agents
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.manager import ManagerAgent
from agents.context_agent import ContextAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ArcSync API",
    description="Context-aware technical specification generator REST API",
    version="2.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Models ──────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    intent: str = Field(..., description="Natural language feature requirement description")
    feature_name: Optional[str] = Field(None, description="Optional feature name")
    repo_path: Optional[str] = Field(None, description="Path to repository to analyze")

class AnchorItem(BaseModel):
    file: str
    tags: List[str] = []
    relevance: float = 0.0
    endpoints: List[str] = []

class GenerateResponse(BaseModel):
    complexity: str = Field(..., description="Complexity as 'N/13'")
    verdict: str = Field("ANALYZING", description="FEASIBLE, FEASIBLE_WITH_CAVEATS, or NOT_FEASIBLE")
    reasoning: str = Field(..., description="Logical reasoning for the assessment")
    anchors: List[AnchorItem] = Field(default_factory=list, description="Matched file anchors")
    specification: str = Field(..., description="Full spec in markdown")
    tech_stack: str = Field("Unknown", description="Detected tech stack")
    database: str = Field("Unknown", description="Detected database")

class HealthResponse(BaseModel):
    status: str
    backend_connected: bool
    message: str
    tech_stack: str = "Unknown"
    database: str = "Unknown"
    file_count: int = 0
    api_endpoints: int = 0

class RepoInfo(BaseModel):
    name: str
    path: str
    description: str

# ── Available Sample Repos ────────────────────────────────────────────────────

def get_available_repos():
    """Get list of available repositories including custom ones."""
    repos = []
    
    # Only add sample repos if they exist on disk
    ecommerce_path = Path(__file__).parent.parent / "sample_repos" / "ecommerce-api"
    if ecommerce_path.exists():
        repos.append({
            "name": "E-Commerce API",
            "path": str(ecommerce_path),
            "description": "Node.js/Express + MongoDB e-commerce REST API"
        })
    
    # Always include self-analysis
    repos.append({
        "name": "ArcSync (Self)",
        "path": str(Path(__file__).parent.parent),
        "description": "This project — Python/FastAPI multi-agent system"
    })
    
    # Check for custom repos in test_repos directory
    test_repos_dir = Path(__file__).parent.parent / "test_repos"
    if test_repos_dir.exists():
        for repo_dir in test_repos_dir.iterdir():
            if repo_dir.is_dir() and not repo_dir.name.startswith('.'):
                repos.append({
                    "name": f"Test: {repo_dir.name}",
                    "path": str(repo_dir),
                    "description": f"Custom test repository: {repo_dir.name}"
                })
    
    return repos

SAMPLE_REPOS = get_available_repos()

# ── Upload Directory Setup ───────────────────────────────────────────────────

# Use /tmp for uploads on Vercel (read-only filesystem)
if os.environ.get("VERCEL"):
    UPLOAD_DIR = Path("/tmp/uploaded_repos")
else:
    UPLOAD_DIR = Path(__file__).parent.parent / "uploaded_repos"
try:
    UPLOAD_DIR.mkdir(exist_ok=True)
except OSError:
    UPLOAD_DIR = Path("/tmp/uploaded_repos")
    UPLOAD_DIR.mkdir(exist_ok=True)

def detect_repo_name(repo_path: Path) -> str:
    """Detect repository name from package.json, README, or directory name."""
    # Try package.json
    package_json = repo_path / "package.json"
    if package_json.exists():
        try:
            with open(package_json) as f:
                data = json.load(f)
                if "name" in data:
                    return data["name"]
        except:
            pass
    
    # Try README
    for readme in ["README.md", "README.txt", "README"]:
        readme_path = repo_path / readme
        if readme_path.exists():
            try:
                with open(readme_path) as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("#"):
                        return first_line.lstrip("#").strip()
            except:
                pass
    
    # Fallback to directory name
    return repo_path.name

# ── Agent State ──────────────────────────────────────────────────────────────

_agents: Dict[str, dict] = {}

def get_agents(repo_path: str = None) -> dict:
    """Get or initialize agents for a given repo path."""
    global _agents

    if repo_path is None:
        repo_path = SAMPLE_REPOS[0]["path"]

    if repo_path not in _agents:
        logger.info(f"Initializing agents for: {repo_path}")
        try:
            manager = ManagerAgent(repo_path=repo_path)
            context = ContextAgent(repo_path=repo_path)
            _agents[repo_path] = {
                "manager": manager,
                "context": context,
            }
            logger.info(f"Agents initialized for: {repo_path}")
        except Exception as e:
            logger.error(f"Failed to initialize agents for {repo_path}: {e}")
            raise

    return _agents[repo_path]


def parse_spec_response(spec_markdown: str) -> dict:
    """Parse the specification to extract structured fields."""
    # Extract verdict
    verdict = "FEASIBLE"
    verdict_match = re.search(r'(FEASIBLE_WITH_CAVEATS|NOT_FEASIBLE|FEASIBLE)', spec_markdown)
    if verdict_match:
        verdict = verdict_match.group(1)

    # Extract complexity
    complexity = "5/13"
    complexity_match = re.search(r'`(\d+)/13`', spec_markdown)
    if complexity_match:
        complexity = f"{complexity_match.group(1)}/13"

    # Extract reasoning (first paragraph after "Analysis" or "Feasibility")
    reasoning = "Analysis grounded in repository context via IBM Bob."
    reasoning_patterns = [
        r"###?\s*(?:Feasibility|Analysis|Bob's Analysis).*?\n((?:(?!###?).*\n)*)",
        r"\*\*Analysis\*\*:\s*(.*?)(?:\n\n|\n###)",
    ]
    for pattern in reasoning_patterns:
        match = re.search(pattern, spec_markdown, re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Clean up markdown formatting
            text = re.sub(r'\*\*', '', text)
            text = re.sub(r'`', '', text)
            if len(text) > 20:
                reasoning = text[:500]
                break

    return {
        "verdict": verdict,
        "complexity": complexity,
        "reasoning": reasoning,
    }


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/v1/repos")
async def list_repos():
    """List available repositories to analyze."""
    return SAMPLE_REPOS


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check(repo_path: str = None):
    """Health check with repository context information."""
    try:
        if repo_path is None:
            repo_path = SAMPLE_REPOS[0]["path"]

        agents = get_agents(repo_path)
        constraints = agents["context"].get_grounding_constraints()

        return HealthResponse(
            status="healthy",
            backend_connected=True,
            message=f"IBM Bob connected. Analyzing: {Path(repo_path).name}",
            tech_stack=constraints.get("tech_stack", "Unknown"),
            database=constraints.get("database", "Unknown"),
            file_count=constraints.get("file_count", 0),
            api_endpoints=constraints.get("api_endpoints", 0),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            backend_connected=False,
            message=f"Backend issue: {str(e)}"
        )


@app.post("/api/v1/generate")
async def generate_specification(request: GenerateRequest):
    """Generate a context-aware technical specification."""
    try:
        logger.info(f"Generate request: '{request.intent[:80]}...' repo={request.repo_path}")

        if not request.intent or len(request.intent.strip()) < 5:
            raise HTTPException(status_code=400, detail="Intent must be at least 5 characters")

        repo_path = request.repo_path or SAMPLE_REPOS[0]["path"]
        agents = get_agents(repo_path)
        manager = agents["manager"]

        feature_name = request.feature_name or "Feature Specification"

        # Generate the spec
        spec_markdown = manager.orchestrate_spec_request(feature_name, request.intent)

        # Parse structured fields from the spec
        parsed = parse_spec_response(spec_markdown)

        # Build anchor list from retriever
        retriever = manager.retriever
        raw_anchors = retriever.get_prompt_context(request.intent)
        anchors = []
        for a in raw_anchors:
            endpoints = [f"{e['method']} {e['path']}" for e in a.get('api_endpoints', [])]
            anchors.append(AnchorItem(
                file=a['file'],
                tags=a.get('tags', []),
                relevance=a.get('relevance', 0),
                endpoints=endpoints,
            ))

        # Get repo metadata
        metadata = retriever.get_metadata()

        response = GenerateResponse(
            complexity=parsed["complexity"],
            verdict=parsed["verdict"],
            reasoning=parsed["reasoning"],
            anchors=anchors,
            specification=spec_markdown,
            tech_stack=metadata.get("tech_stack", "Unknown"),
            database=metadata.get("database", "Unknown"),
        )

        logger.info(f"Spec generated — verdict={parsed['verdict']}, complexity={parsed['complexity']}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/v1/export")
async def export_audit():
    """Export the IBM Bob session audit log."""
    log_dir = Path("logs/ibm_bob_audit")
    if not log_dir.exists():
        raise HTTPException(status_code=404, detail="No audit logs found")

    # Find the most recent log file
    log_files = sorted(log_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not log_files:
        raise HTTPException(status_code=404, detail="No audit logs found")

    # Combine all session logs
    all_entries = []
    for lf in log_files[:5]:
        try:
            with open(lf, 'r') as f:
                for line in f:
                    if line.strip():
                        all_entries.append(json.loads(line))
        except Exception:
            pass

    return JSONResponse(content={
        "export_format": "IBM Bob Audit Report",
        "total_entries": len(all_entries),
        "entries": all_entries
    })


@app.post("/api/v1/upload-repo")
async def upload_repository(file: UploadFile = File(...)):
    """
    Upload a repository as a ZIP file for analysis.
    Returns the path to the extracted repository.
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")
        
        # Validate file size (50MB max)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB")
        
        # Generate unique ID
        repo_id = f"repo_{uuid.uuid4().hex[:8]}"
        repo_path = UPLOAD_DIR / repo_id
        
        # Save ZIP temporarily
        zip_path = UPLOAD_DIR / f"{repo_id}.zip"
        with open(zip_path, 'wb') as f:
            f.write(content)
        
        # Extract ZIP with security checks
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check for path traversal attacks
                for member in zip_ref.namelist():
                    if member.startswith('/') or '..' in member:
                        raise HTTPException(status_code=400, detail="Invalid ZIP file structure")
                
                # Extract to repo directory
                zip_ref.extractall(repo_path)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid or corrupted ZIP file")
        finally:
            # Clean up ZIP file
            if zip_path.exists():
                zip_path.unlink()
        
        # Find the actual repo root (handle single-folder ZIPs)
        subdirs = [d for d in repo_path.iterdir() if d.is_dir()]
        if len(subdirs) == 1 and not any(repo_path.glob('*.json')):
            # Move contents up one level
            temp_dir = repo_path.parent / f"{repo_id}_temp"
            subdirs[0].rename(temp_dir)
            shutil.rmtree(repo_path)
            temp_dir.rename(repo_path)
        
        # Detect repo name
        repo_name = detect_repo_name(repo_path)
        
        # Add to global repos list
        new_repo = {
            "name": f"📤 {repo_name}",
            "path": str(repo_path),
            "description": f"Uploaded repository: {repo_name}",
            "uploaded": True
        }
        
        logger.info(f"Repository uploaded: {repo_name} at {repo_path}")
        
        return new_repo
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        # Cleanup on error
        if 'repo_path' in locals() and repo_path.exists():
            shutil.rmtree(repo_path, ignore_errors=True)
        if 'zip_path' in locals() and zip_path.exists():
            zip_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.delete("/api/v1/repos/{repo_id}")
async def delete_uploaded_repo(repo_id: str):
    """Delete an uploaded repository."""
    try:
        repo_path = UPLOAD_DIR / repo_id
        if not repo_path.exists():
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Remove from agents cache if loaded
        if str(repo_path) in _agents:
            del _agents[str(repo_path)]
        
        # Delete directory
        shutil.rmtree(repo_path)
        
        logger.info(f"Deleted uploaded repository: {repo_id}")
        return {"status": "deleted", "repo_id": repo_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


# ── Static File Serving ──────────────────────────────────────────────────────

static_dir = Path(__file__).parent

@app.get("/")
async def read_index():
    """Serve the main HTML interface."""
    index_path = static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(index_path))

@app.get("/script.js")
async def serve_script():
    """Serve the JavaScript file."""
    js_path = static_dir / "script.js"
    if not js_path.exists():
        raise HTTPException(status_code=404, detail="script.js not found")
    return FileResponse(str(js_path), media_type="application/javascript")

try:
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
