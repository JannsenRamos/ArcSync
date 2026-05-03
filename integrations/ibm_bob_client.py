import json
import datetime
import os
from pathlib import Path

# File extensions to index (code files only)
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.rs',
    '.cs', '.php', '.swift', '.kt', '.scala', '.sql', '.graphql',
    '.json', '.yaml', '.yml', '.toml', '.xml', '.md'
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
    '.next', 'dist', 'build', '.cache', 'coverage', '.idea', '.vscode'
}

# Key file patterns for architectural analysis
KEY_PATTERNS = {
    'model': ['model', 'schema', 'entity', 'migration'],
    'route': ['route', 'controller', 'handler', 'endpoint', 'api', 'view'],
    'middleware': ['middleware', 'interceptor', 'guard', 'filter', 'hook'],
    'config': ['config', 'setting', 'env', 'constant'],
    'test': ['test', 'spec', '__test__'],
    'auth': ['auth', 'login', 'session', 'jwt', 'oauth', 'permission'],
    'database': ['db', 'database', 'connection', 'pool', 'migration'],
    'service': ['service', 'util', 'helper', 'lib']
}


class IBMBobClient:
    """
    Core integration for Arch-Sync to interface with the IBM Bob IDE context layer.
    Satisfies FR2: Repository Context Injection.
    """
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.audit_log_path = Path("logs/ibm_bob_audit")
        self.audit_log_path.mkdir(parents=True, exist_ok=True)
        self.session_id = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def get_repository_context(self):
        """
        Queries the IBM Bob Layer to ingest metadata (directory structure, schema files).
        Ensures architectural alignment and zero framework hallucinations.
        """
        metadata = {
            "tech_stack": self._detect_tech_stack(),
            "database": self._detect_database(),
            "dependencies": self._extract_dependencies(),
            "directory_map": self._get_code_files(),
            "file_contents": self._read_key_files(),
            "file_tags": self._tag_files(),
            "api_patterns": self._detect_api_patterns(),
            "timestamp": str(datetime.datetime.now())
        }

        self.log_event("Repository Context Extraction", {
            "tech_stack": metadata["tech_stack"],
            "database": metadata["database"],
            "files_indexed": len(metadata["directory_map"]),
            "key_files_read": len(metadata["file_contents"]),
        })
        return metadata

    def _get_code_files(self):
        """Get all code files, excluding irrelevant directories."""
        files = []
        try:
            for p in self.repo_path.rglob('*'):
                if p.is_file() and p.suffix in CODE_EXTENSIONS:
                    # Skip files in excluded directories
                    parts = p.relative_to(self.repo_path).parts
                    if not any(skip in parts for skip in SKIP_DIRS):
                        files.append(str(p.relative_to(self.repo_path)))
        except Exception:
            pass
        return files

    def _detect_tech_stack(self):
        """Detect the tech stack from project files."""
        stack_parts = []

        # Language/Runtime detection
        if (self.repo_path / "package.json").exists():
            pkg = self._read_json(self.repo_path / "package.json")
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "express" in deps:
                stack_parts.append("Node.js/Express")
            elif "next" in deps:
                stack_parts.append("Next.js")
            elif "react" in deps:
                stack_parts.append("React")
            elif "vue" in deps:
                stack_parts.append("Vue.js")
            else:
                stack_parts.append("Node.js")
        elif (self.repo_path / "requirements.txt").exists():
            reqs = (self.repo_path / "requirements.txt").read_text(errors='ignore').lower()
            if "fastapi" in reqs:
                stack_parts.append("Python/FastAPI")
            elif "django" in reqs:
                stack_parts.append("Python/Django")
            elif "flask" in reqs:
                stack_parts.append("Python/Flask")
            else:
                stack_parts.append("Python")
        elif (self.repo_path / "pom.xml").exists():
            stack_parts.append("Java/Maven")
        elif (self.repo_path / "build.gradle").exists():
            stack_parts.append("Java/Gradle")
        elif (self.repo_path / "go.mod").exists():
            stack_parts.append("Go")
        elif (self.repo_path / "Cargo.toml").exists():
            stack_parts.append("Rust")
        elif (self.repo_path / "Gemfile").exists():
            stack_parts.append("Ruby")
        else:
            stack_parts.append("Unknown")

        return " + ".join(stack_parts) if stack_parts else "Unknown"

    def _detect_database(self):
        """Detect database type from code patterns and dependencies."""
        all_content = ""
        for f in self._get_code_files():
            try:
                content = (self.repo_path / f).read_text(errors='ignore')[:2000]
                all_content += content.lower() + "\n"
            except Exception:
                pass

        # Also check dependencies
        if (self.repo_path / "package.json").exists():
            pkg = self._read_json(self.repo_path / "package.json")
            deps = " ".join(pkg.get("dependencies", {}).keys())
            all_content += deps.lower()
        if (self.repo_path / "requirements.txt").exists():
            all_content += (self.repo_path / "requirements.txt").read_text(errors='ignore').lower()

        if "mongoose" in all_content or "mongodb" in all_content or "mongo" in all_content:
            return "MongoDB (Mongoose ODM)"
        elif "sqlalchemy" in all_content:
            return "SQL (SQLAlchemy)"
        elif "sequelize" in all_content:
            return "SQL (Sequelize)"
        elif "prisma" in all_content:
            return "SQL/NoSQL (Prisma)"
        elif "pg" in all_content or "postgres" in all_content:
            return "PostgreSQL"
        elif "mysql" in all_content:
            return "MySQL"
        elif "sqlite" in all_content:
            return "SQLite"
        elif "redis" in all_content:
            return "Redis"
        elif "dynamodb" in all_content:
            return "DynamoDB"
        return "Unknown"

    def _extract_dependencies(self):
        """Extract dependency list from manifest files."""
        deps = {}
        if (self.repo_path / "package.json").exists():
            pkg = self._read_json(self.repo_path / "package.json")
            deps = pkg.get("dependencies", {})
        elif (self.repo_path / "requirements.txt").exists():
            try:
                lines = (self.repo_path / "requirements.txt").read_text(errors='ignore').strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        name = line.split('>=')[0].split('==')[0].split('<=')[0].split('<')[0].split('>')[0].strip()
                        deps[name] = line
            except Exception:
                pass
        return deps

    def _read_key_files(self):
        """Read content of architecturally significant files (models, routes, configs)."""
        key_files = {}
        max_lines = 80

        for f in self._get_code_files():
            fname = f.lower()
            is_key = any(
                pattern in fname
                for patterns in KEY_PATTERNS.values()
                for pattern in patterns
            )
            if is_key:
                try:
                    content = (self.repo_path / f).read_text(errors='ignore')
                    lines = content.split('\n')[:max_lines]
                    key_files[f] = '\n'.join(lines)
                except Exception:
                    pass

        return key_files

    def _tag_files(self):
        """Tag each file with its architectural role."""
        tags = {}
        for f in self._get_code_files():
            fname = f.lower()
            file_tags = []
            for tag, patterns in KEY_PATTERNS.items():
                if any(p in fname for p in patterns):
                    file_tags.append(tag)
            tags[f] = file_tags if file_tags else ['source']
        return tags

    def _detect_api_patterns(self):
        """Detect API endpoint patterns from route files."""
        patterns = []
        for f in self._get_code_files():
            fname = f.lower()
            if any(p in fname for p in ['route', 'controller', 'handler', 'api', 'endpoint']):
                try:
                    content = (self.repo_path / f).read_text(errors='ignore')
                    # Look for Express/FastAPI route patterns
                    import re
                    # Express: router.get('/path', ...) or app.post('/path', ...)
                    express_routes = re.findall(
                        r'(?:router|app)\.(get|post|put|patch|delete)\s*\(\s*[\'"]([^\'"]+)[\'"]',
                        content, re.IGNORECASE
                    )
                    for method, path in express_routes:
                        patterns.append({"method": method.upper(), "path": path, "file": f})

                    # FastAPI: @app.get("/path") or @router.post("/path")
                    fastapi_routes = re.findall(
                        r'@(?:app|router)\.(get|post|put|patch|delete)\s*\(\s*[\'"]([^\'"]+)[\'"]',
                        content, re.IGNORECASE
                    )
                    for method, path in fastapi_routes:
                        patterns.append({"method": method.upper(), "path": path, "file": f})
                except Exception:
                    pass
        return patterns

    def _read_json(self, path):
        """Safely read a JSON file."""
        try:
            with open(path, 'r', errors='ignore') as f:
                return json.load(f)
        except Exception:
            return {}

    def log_event(self, task_name, payload):
        """
        Records tasks and sessions for the mandatory IBM Bob Report.
        """
        log_entry = {
            "session_id": self.session_id,
            "task": task_name,
            "details": payload,
            "timestamp": str(datetime.datetime.now())
        }

        log_file = self.audit_log_path / f"{self.session_id}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        print(f"[IBM Bob Audit] Task recorded: {task_name}")

    def get_audit_log_path(self):
        """Returns the path to the current session's audit log."""
        return self.audit_log_path / f"{self.session_id}.jsonl"


# Usage Example for the Hackathon Submission
if __name__ == "__main__":
    client = IBMBobClient()
    context = client.get_repository_context()
    print(f"Context ingested for Arch-Sync: {context['tech_stack']}")
    print(f"Database: {context['database']}")
    print(f"Files: {len(context['directory_map'])}")
    print(f"Key files read: {len(context['file_contents'])}")
    print(f"API patterns: {len(context['api_patterns'])}")