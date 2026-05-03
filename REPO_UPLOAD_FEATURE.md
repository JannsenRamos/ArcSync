# Repository Upload Feature

## Overview
This document describes how to enable users to upload their own repositories for testing with ArcSync, instead of being limited to the sample repositories.

## Implementation Strategy

### 1. Backend Changes (server.py)

#### Add Upload Endpoint
```python
@app.post("/api/v1/upload-repo")
async def upload_repository(file: UploadFile = File(...)):
    """
    Upload a repository as a ZIP file for analysis.
    Returns the path to the extracted repository.
    """
```

#### Add Cleanup Endpoint
```python
@app.delete("/api/v1/repos/{repo_id}")
async def delete_uploaded_repo(repo_id: str):
    """Remove an uploaded repository from the system."""
```

### 2. Frontend Changes

#### HTML (index.html)
- Add upload button in repository selector area
- Add modal/dialog for file upload
- Show upload progress indicator
- Display uploaded repos in the selector

#### JavaScript (script.js)
- Handle file selection and validation
- Upload ZIP file via FormData
- Update repo list after successful upload
- Handle errors gracefully

### 3. File Structure

```
ArcSync/
├── uploaded_repos/          # New directory for user uploads
│   ├── repo_abc123/        # Extracted repo (UUID-based naming)
│   ├── repo_def456/
│   └── ...
├── sample_repos/           # Existing sample repos
└── test_repos/             # Test repos (already supported)
```

## Implementation Details

### Backend Upload Handler

```python
import zipfile
import uuid
import shutil
from fastapi import UploadFile, File

UPLOAD_DIR = Path(__file__).parent.parent / "uploaded_repos"
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/v1/upload-repo")
async def upload_repository(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith('.zip'):
        raise HTTPException(400, "Only ZIP files are supported")
    
    # Generate unique ID
    repo_id = f"repo_{uuid.uuid4().hex[:8]}"
    repo_path = UPLOAD_DIR / repo_id
    
    # Save and extract
    zip_path = UPLOAD_DIR / f"{repo_id}.zip"
    with open(zip_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    
    # Extract ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(repo_path)
    
    # Clean up ZIP
    zip_path.unlink()
    
    # Detect repo name from extracted content
    repo_name = detect_repo_name(repo_path)
    
    return {
        "repo_id": repo_id,
        "name": repo_name,
        "path": str(repo_path),
        "description": f"Uploaded repository: {repo_name}"
    }
```

### Frontend Upload UI

```javascript
// Add to script.js
async function uploadRepository() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.zip';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        showToast('Uploading repository...', 'info');
        
        try {
            const res = await fetch(`${API_BASE}/api/v1/upload-repo`, {
                method: 'POST',
                body: formData
            });
            
            if (!res.ok) throw new Error('Upload failed');
            
            const data = await res.json();
            repos.push(data);
            renderRepoSelector();
            selectRepo(repos.length - 1);
            
            showToast('✓ Repository uploaded successfully!', 'success');
        } catch (err) {
            showToast(`Upload failed: ${err.message}`, 'error');
        }
    };
    
    input.click();
}
```

### HTML Upload Button

```html
<!-- Add to repository selector section -->
<button onclick="uploadRepository()" 
        class="px-4 py-2 rounded-lg text-sm font-medium bg-accent text-white hover:bg-accent-light transition-all flex items-center gap-2">
    <span class="material-symbols-outlined text-sm">upload_file</span>
    Upload Repo
</button>
```

## Security Considerations

1. **File Size Limits**: Limit upload size to prevent abuse (e.g., 50MB max)
2. **File Type Validation**: Only accept ZIP files
3. **Content Scanning**: Validate extracted content structure
4. **Path Traversal**: Prevent malicious ZIP files with path traversal
5. **Cleanup**: Implement automatic cleanup of old uploaded repos
6. **Rate Limiting**: Limit uploads per user/session

## User Experience Flow

1. User clicks "Upload Repo" button
2. File picker opens (accepts .zip only)
3. User selects repository ZIP file
4. Progress indicator shows upload status
5. Backend extracts and validates repository
6. New repo appears in selector dropdown
7. User can immediately test with uploaded repo
8. Optional: User can delete uploaded repos

## Alternative: GitHub URL Import

Instead of ZIP upload, could also support:

```python
@app.post("/api/v1/import-github")
async def import_from_github(github_url: str):
    """Clone a public GitHub repository for analysis."""
    # Use git clone or GitHub API
    # Extract repo name from URL
    # Clone to uploaded_repos directory
    # Return repo info
```

## Testing Instructions

1. Create a test ZIP file of a small repository
2. Upload via the UI
3. Verify it appears in repo selector
4. Generate a spec using the uploaded repo
5. Verify IBM Bob can analyze the uploaded code
6. Test cleanup/deletion functionality

## Benefits

- **Flexibility**: Users can test with their actual codebases
- **Real-world Testing**: More accurate feasibility assessments
- **Demo Value**: Shows the system works with any repository
- **Hackathon Appeal**: Judges can test with their own projects

## Current Workaround

Until this feature is implemented, users can:

1. Manually copy their repo to `test_repos/` directory
2. Restart the server
3. The repo will appear in the selector automatically

Example:
```bash
# Copy your repo
cp -r /path/to/your/repo ./test_repos/my-project

# Restart server
python static/server.py
```

The system already supports this via the `get_available_repos()` function in server.py (lines 81-109).

## Implementation Priority

**Phase 1 (Quick Win):**
- Document the manual copy workaround ✓
- Improve UI messaging about test_repos support

**Phase 2 (Full Feature):**
- Implement ZIP upload endpoint
- Add upload UI component
- Add validation and security checks

**Phase 3 (Enhanced):**
- GitHub URL import
- Drag-and-drop upload
- Repository management dashboard
- Automatic cleanup of old uploads

## Conclusion

The repository upload feature significantly enhances ArcSync's usability and demo value. The manual workaround provides immediate functionality, while the full implementation can be added post-hackathon for production use.