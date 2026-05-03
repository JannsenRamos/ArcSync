#!/usr/bin/env python3
"""
Quick test script to verify repository upload functionality.
Creates a test ZIP and simulates an upload.
"""

import zipfile
import tempfile
import os
from pathlib import Path

def create_test_repo_zip():
    """Create a minimal test repository ZIP file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / "test-repo"
        repo_dir.mkdir()
        
        # Create sample files
        (repo_dir / "README.md").write_text("# Test Repository\n\nThis is a test repo for upload.")
        (repo_dir / "package.json").write_text('{\n  "name": "test-repo",\n  "version": "1.0.0"\n}')
        
        # Create a simple API file
        api_dir = repo_dir / "src"
        api_dir.mkdir()
        (api_dir / "app.js").write_text("""
const express = require('express');
const app = express();

app.get('/api/users', (req, res) => {
    res.json({ users: [] });
});

app.listen(3000);
""")
        
        # Create ZIP
        zip_path = Path("test-repo.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in repo_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(repo_dir.parent)
                    zipf.write(file, arcname)
        
        return zip_path

def main():
    print("[TEST] Creating test repository ZIP...")
    zip_path = create_test_repo_zip()
    
    print(f"[OK] Created: {zip_path}")
    print(f"[INFO] Size: {zip_path.stat().st_size / 1024:.2f} KB")
    
    print("\n[INSTRUCTIONS] Test Instructions:")
    print("1. Start the server: python static/server.py")
    print("2. Open http://localhost:8000")
    print("3. Click 'Upload ZIP' button")
    print(f"4. Select the file: {zip_path.absolute()}")
    print("5. Verify it appears in the repository selector")
    print("6. Try generating a spec with the uploaded repo")
    
    print("\n[VERIFY] Manual verification:")
    print("- Check that uploaded_repos/ directory is created")
    print("- Verify repo appears with upload icon")
    print("- Test spec generation works with uploaded repo")
    print("- Check IBM Bob can analyze the uploaded files")
    
    print(f"\n[CLEANUP] To remove test file: del {zip_path}")

if __name__ == "__main__":
    main()

# Made with Bob
