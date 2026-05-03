# How to Upload Your Own Repository to ArcSync

## Quick Start

ArcSync now supports uploading your own repositories for testing! You can upload any codebase as a ZIP file and immediately test feature specifications against it.

## Method 1: Upload via Web UI (Recommended)

### Step 1: Prepare Your Repository

1. **Create a ZIP file** of your repository:
   ```bash
   # On Linux/Mac
   cd /path/to/your/project
   zip -r my-project.zip . -x "*.git*" -x "*node_modules*" -x "*venv*"
   
   # On Windows (PowerShell)
   Compress-Archive -Path . -DestinationPath my-project.zip
   ```

2. **Exclude unnecessary files** to keep the ZIP small:
   - `.git` directory
   - `node_modules/` or `venv/` directories
   - Build artifacts (`dist/`, `build/`, `target/`)
   - Large binary files
   - IDE settings (`.vscode/`, `.idea/`)

3. **Keep it under 50MB** - The system has a 50MB upload limit

### Step 2: Upload via UI

1. **Start the ArcSync server**:
   ```bash
   python static/server.py
   ```

2. **Open the web interface**: http://localhost:8000

3. **Click "Upload ZIP"** button in the repository selector area

4. **Select your ZIP file** from the file picker

5. **Wait for upload** - You'll see a progress notification

6. **Your repo appears** in the selector with a 📤 icon

### Step 3: Test Your Repository

1. **Select your uploaded repo** from the dropdown
2. **Enter a feature description** in the text area
3. **Click "Process Requirements"**
4. **Review the generated specification** grounded in your actual codebase!

## Method 2: Manual Copy (Alternative)

If you prefer not to create a ZIP file, you can manually copy your repository:

```bash
# Create test_repos directory if it doesn't exist
mkdir -p test_repos

# Copy your repository
cp -r /path/to/your/project test_repos/my-project

# Restart the server
python static/server.py
```

Your repository will automatically appear in the selector.

## What Happens During Upload?

1. **Validation**: System checks file type and size
2. **Extraction**: ZIP is extracted to `uploaded_repos/repo_xxxxxxxx/`
3. **Analysis**: IBM Bob scans the repository structure
4. **Indexing**: Files are indexed for context retrieval
5. **Ready**: Repository is available for specification generation

## Supported Repository Types

ArcSync works with any text-based codebase:

- ✅ **Node.js/JavaScript** (Express, React, Vue, etc.)
- ✅ **Python** (Django, Flask, FastAPI, etc.)
- ✅ **Java/Kotlin** (Spring Boot, etc.)
- ✅ **Go** (Gin, Echo, etc.)
- ✅ **Ruby** (Rails, Sinatra, etc.)
- ✅ **PHP** (Laravel, Symfony, etc.)
- ✅ **C#/.NET** (ASP.NET, etc.)
- ✅ **Any other text-based code**

## Best Practices

### For Best Results:

1. **Include README files** - Helps IBM Bob understand your project
2. **Keep package.json/requirements.txt** - Identifies dependencies
3. **Include API routes/controllers** - Enables endpoint detection
4. **Add database models** - Improves feasibility analysis
5. **Keep code organized** - Clear structure = better analysis

### What to Exclude:

- ❌ Binary files (images, videos, executables)
- ❌ Dependencies (node_modules, venv, vendor)
- ❌ Build outputs (dist, build, target)
- ❌ Git history (.git directory)
- ❌ IDE settings (.vscode, .idea)
- ❌ Log files and temporary files

## Example: Uploading an E-commerce API

```bash
# 1. Navigate to your project
cd ~/projects/my-ecommerce-api

# 2. Create a clean ZIP (excluding dependencies)
zip -r ecommerce-api.zip . \
  -x "node_modules/*" \
  -x ".git/*" \
  -x "*.log" \
  -x ".env"

# 3. Upload via UI
# - Open http://localhost:8000
# - Click "Upload ZIP"
# - Select ecommerce-api.zip
# - Wait for confirmation

# 4. Test a feature
# Feature: "Add Stripe payment integration with webhook support"
# ArcSync will analyze your actual routes, models, and middleware!
```

## Managing Uploaded Repositories

### View Uploaded Repos
All uploaded repositories appear in the selector with a 📤 icon.

### Delete Uploaded Repos
Currently, uploaded repos persist until manually deleted from the `uploaded_repos/` directory:

```bash
# List uploaded repos
ls uploaded_repos/

# Delete a specific repo
rm -rf uploaded_repos/repo_abc12345
```

**Note**: A delete button in the UI is planned for future releases.

## Troubleshooting

### "File too large" Error
- **Solution**: Reduce ZIP size by excluding dependencies and build artifacts
- **Limit**: 50MB maximum

### "Invalid ZIP file" Error
- **Solution**: Ensure you're uploading a valid ZIP file
- **Check**: Try extracting the ZIP manually first

### "Upload failed" Error
- **Check**: Server logs for detailed error messages
- **Verify**: You have write permissions in the project directory
- **Try**: Restart the server and try again

### Repository Not Appearing
- **Refresh**: Reload the page
- **Check**: `uploaded_repos/` directory exists and contains your repo
- **Verify**: No errors in server console

## Security Notes

- ✅ Only ZIP files are accepted
- ✅ 50MB size limit enforced
- ✅ Path traversal attacks prevented
- ✅ Files are scanned for malicious content
- ⚠️ Don't upload sensitive data (API keys, passwords, etc.)
- ⚠️ Uploaded repos are stored locally on the server

## API Reference

For programmatic uploads:

```bash
# Upload a repository
curl -X POST http://localhost:8000/api/v1/upload-repo \
  -F "file=@my-project.zip"

# Response:
{
  "name": "📤 my-project",
  "path": "/path/to/uploaded_repos/repo_abc12345",
  "description": "Uploaded repository: my-project",
  "uploaded": true
}
```

## Demo Repositories

ArcSync includes sample repositories for testing:

1. **E-Commerce API** - Node.js/Express + MongoDB
2. **ArcSync (Self)** - Python/FastAPI multi-agent system

You can use these to understand how the system works before uploading your own.

## Next Steps

After uploading your repository:

1. ✅ Test with simple features first
2. ✅ Review the generated specifications
3. ✅ Check the "Structural Anchors" to see what files IBM Bob found
4. ✅ Iterate on your feature descriptions
5. ✅ Export the IBM Bob audit report for documentation

## Need Help?

- 📖 Check `REPO_UPLOAD_FEATURE.md` for technical details
- 🐛 Report issues on GitHub
- 💬 Ask questions in the discussion forum

---

**Happy Testing! 🚀**

Upload your repository and see how ArcSync generates context-aware specifications grounded in your actual codebase.