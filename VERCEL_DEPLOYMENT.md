# 🚀 Deploying ArcSync to Vercel

This guide will help you deploy the ArcSync web application to Vercel.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional): Install with `npm i -g vercel`
3. **IBM Watsonx Credentials**:
   - IBM API Key
   - Watsonx Project ID
   - Watsonx URL (default: https://us-south.ml.cloud.ibm.com)

## 🎯 Deployment Methods

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Project"
   - Select your GitHub repository
   - Vercel will auto-detect the configuration from `vercel.json`

3. **Configure Environment Variables**
   
   In the Vercel dashboard, add these environment variables:
   
   | Variable Name | Value | Description |
   |--------------|-------|-------------|
   | `IBM_API_KEY` | `your_ibm_api_key` | Your IBM Cloud API key |
   | `WATSONX_PROJECT_ID` | `your_project_id` | Your Watsonx project ID |
   | `WATSONX_URL` | `https://us-south.ml.cloud.ibm.com` | Watsonx API endpoint |

4. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete (2-3 minutes)
   - Your app will be live at `https://your-project.vercel.app`

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Set Environment Variables**
   ```bash
   vercel env add IBM_API_KEY
   vercel env add WATSONX_PROJECT_ID
   vercel env add WATSONX_URL
   ```
   
   Enter the values when prompted.

4. **Deploy**
   ```bash
   # Deploy to preview
   vercel
   
   # Deploy to production
   vercel --prod
   ```

## 📁 Deployment Structure

The deployment uses the following structure:

```
ArcSync/
├── api/
│   └── index.py          # Vercel serverless entry point
├── static/
│   ├── server.py         # FastAPI application
│   ├── index.html        # Frontend UI
│   └── script.js         # Frontend logic
├── agents/               # Multi-agent system
├── core/                 # Core functionality
├── integrations/         # IBM integrations
├── vercel.json          # Vercel configuration
├── .vercelignore        # Files to exclude from deployment
└── requirements.txt     # Python dependencies
```

## ⚙️ Configuration Details

### vercel.json

The `vercel.json` file configures:
- Python runtime for the FastAPI app
- Route handling for API and static files
- Environment variable references

### .vercelignore

Excludes unnecessary files from deployment:
- Test files and sample repositories
- Documentation files
- Log files
- IDE configurations

## 🔒 Security Best Practices

1. **Never commit `.env` files** - Use Vercel's environment variables
2. **Use Vercel Secrets** for sensitive data:
   ```bash
   vercel secrets add ibm-api-key "your_key_here"
   ```
3. **Enable HTTPS** - Vercel provides automatic SSL certificates
4. **Set up CORS** properly in production

## 🐛 Troubleshooting

### Build Fails

**Issue**: Python dependencies fail to install

**Solution**: 
- Check `requirements.txt` for compatibility
- Vercel supports Python 3.9 by default
- Remove any Windows-specific dependencies

### Environment Variables Not Working

**Issue**: App can't access IBM credentials

**Solution**:
1. Verify variables are set in Vercel dashboard
2. Redeploy after adding variables
3. Check variable names match exactly (case-sensitive)

### Static Files Not Loading

**Issue**: CSS/JS files return 404

**Solution**:
- Ensure `static/` directory structure is correct
- Check routes in `vercel.json`
- Verify files aren't in `.vercelignore`

### Cold Start Issues

**Issue**: First request is slow

**Solution**:
- This is normal for serverless functions
- Consider upgrading to Vercel Pro for better performance
- Implement caching strategies

## 📊 Monitoring

### View Logs
```bash
vercel logs [deployment-url]
```

### Check Deployment Status
```bash
vercel ls
```

### View Function Analytics
- Go to Vercel Dashboard → Your Project → Analytics
- Monitor request counts, errors, and performance

## 🔄 Continuous Deployment

Vercel automatically deploys when you push to GitHub:

1. **Production**: Pushes to `main` branch
2. **Preview**: Pushes to other branches or pull requests

Configure branch settings in Vercel Dashboard → Settings → Git

## 🎨 Custom Domain

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. SSL certificate is automatically provisioned

## 📈 Performance Optimization

1. **Enable Edge Caching**
   - Add cache headers in FastAPI responses
   - Use Vercel's Edge Network

2. **Optimize Dependencies**
   - Keep `requirements.txt` minimal
   - Remove unused packages

3. **Use Environment-Specific Configs**
   ```python
   import os
   IS_PRODUCTION = os.getenv('VERCEL_ENV') == 'production'
   ```

## 🆘 Support

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **ArcSync Issues**: [Your GitHub repo]/issues

## ✅ Post-Deployment Checklist

- [ ] Environment variables configured
- [ ] Application loads successfully
- [ ] IBM Bob connection working
- [ ] API endpoints responding
- [ ] File upload functionality tested
- [ ] Export feature working
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up

## 🎉 Success!

Your ArcSync application should now be live on Vercel! 

**Next Steps:**
1. Test all features thoroughly
2. Share the URL with your team
3. Monitor performance and errors
4. Set up custom domain (optional)

---

**Made with ❤️ and deployed on Vercel**