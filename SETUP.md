# 🚀 MediVault Setup Guide

Complete setup instructions for MediVault - from zero to running in 10 minutes!

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.10+** installed
- ✅ **Node.js 18+** and npm installed
- ✅ **Git** installed
- ✅ **Google API Key** ([Get it here](https://makersuite.google.com/app/apikey))
- ✅ **Supabase Account** ([Sign up](https://supabase.com))

### Quick Checks

```bash
# Check Python version
python --version  # Should be 3.10 or higher

# Check Node.js version
node --version  # Should be 18 or higher

# Check npm version
npm --version
```

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/medivault.git
cd medivault
```

### Step 2: Get Google API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the API key

### Step 3: Get Supabase Credentials

1. Sign up at [Supabase](https://supabase.com)
2. Create a new project
3. Go to Settings → API
4. Copy:
   - Project URL
   - Anon/Public key
   - Service role key

### Step 4: Configure Environment

```bash
# Copy example environment file
cp config/.env.example .env

# Edit .env file
# Add your API keys (use any text editor)
nano .env  # or: code .env (VS Code) or: notepad .env (Windows)
```

**Required fields in `.env`:**
```env
GOOGLE_API_KEY=your-google-api-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
```

### Step 5: Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### Step 6: Setup Database

```bash
cd backend
python scripts/setup_database.py
cd ..
```

### Step 7: Run Application

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 8: Access Application

🎉 **Open your browser:** `http://localhost:5173`

---

## 📦 Detailed Installation

### Option A: Manual Installation

#### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import google.generativeai; print('✓ Google AI installed')"
python -c "import chromadb; print('✓ ChromaDB installed')"
python -c "import supabase; print('✓ Supabase installed')"
```

#### 2. AI Pipelines Setup

```bash
# AI pipelines are part of backend, but you can verify:
cd ai_pipelines
python -c "from orchestrator import AgentOrchestrator; print('✓ Agents ready')"
cd ..
```

#### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Verify installation
npm list react
npm list vite
```

#### 4. Database Migration

```bash
cd backend

# Run database setup script
python scripts/setup_database.py

# This will create:
# - users table
# - medical_records table
# - biomarkers table
# - anomalies table
# - doctor_notes table
# - doctor_patient_access table
```

### Option B: Docker Installation

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at:
# - Frontend: http://localhost:5173
# - Backend: http://localhost:5000
```

---

## ⚙️ Configuration

### Environment Variables

Edit `.env` file in root directory:

```env
# ========================================
# Required Configuration
# ========================================

# Google Gemini
GOOGLE_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp
EMBEDDING_MODEL=text-embedding-004

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# ========================================
# Optional Configuration
# ========================================

# Server
FLASK_PORT=5000
FRONTEND_PORT=5173

# Security
JWT_SECRET_KEY=generate-secure-random-string

# Logging
LOG_LEVEL=INFO
LOG_FILE=./data/logs/medivault.log

# Vector Database
VECTOR_DB_PATH=./data/chroma_db
VECTOR_DB_COLLECTION=medical_records
```

### Generate Secure JWT Secret

```bash
# Generate secure random string
python -c "import secrets; print(secrets.token_hex(32))"
```

### Agent Configuration

Edit `ai_pipelines/config.py` to customize:

```python
class AgentConfig:
    # Model selection
    DEFAULT_MODEL = 'gemini-2.0-flash-exp'

    # Temperature settings
    OCR_TEMPERATURE = 0.1      # Very precise
    ANALYSER_TEMPERATURE = 0.4 # More natural

    # Search weights
    HYBRID_SEARCH_WEIGHTS = {
        'semantic': 0.6,
        'keyword': 0.3,
        'recency': 0.1
    }
```

---

## 🧪 Verification

### Test Backend

```bash
# Test health endpoint
curl http://localhost:5000/api/agents/health

# Expected response:
{
  "success": true,
  "status": "healthy",
  "agents": {
    "ocr": "ready",
    "ner": "ready",
    ...
  }
}
```

### Test Agent System

```bash
cd backend
python -m pytest tests/ -v
```

### Test Upload

```bash
# Upload a test document
curl -X POST http://localhost:5000/api/agents/upload \
  -F "file=@test_document.pdf" \
  -F "patient_id=test-123"
```

### Test Frontend

Open browser to `http://localhost:5173` and verify:
- ✅ Dashboard loads
- ✅ Upload page works
- ✅ Search page loads

---

## 🐛 Troubleshooting

### Issue: "GOOGLE_API_KEY not found"

**Solution:**
```bash
# 1. Check .env file exists
ls .env

# 2. Verify GOOGLE_API_KEY is set
cat .env | grep GOOGLE_API_KEY

# 3. Ensure .env is in root directory (not in subdirectories)
pwd  # Should show /path/to/medivault
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall

cd ../frontend
npm install
```

### Issue: "Port already in use"

**Solution:**
```bash
# Find process using port
# On Windows:
netstat -ano | findstr :5000

# On macOS/Linux:
lsof -i :5000

# Kill the process and restart
```

### Issue: "Supabase connection failed"

**Solution:**
```bash
# 1. Verify credentials
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY

# 2. Test connection
python -c "from supabase import create_client; client = create_client('YOUR_URL', 'YOUR_KEY'); print('Connected!')"

# 3. Check if Supabase project is active
```

### Issue: "ChromaDB initialization error"

**Solution:**
```bash
# Clear ChromaDB directory
rm -rf data/chroma_db
mkdir -p data/chroma_db

# Restart backend
```

### Issue: Frontend build errors

**Solution:**
```bash
cd frontend

# Clear cache
rm -rf node_modules package-lock.json
npm cache clean --force

# Reinstall
npm install
```

---

## 🔄 Update Instructions

### Update Backend

```bash
cd backend
git pull
pip install -r requirements.txt --upgrade
```

### Update Frontend

```bash
cd frontend
git pull
npm install
```

### Update AI Agents

```bash
cd ai_pipelines
git pull
# Agents automatically reload on next request
```

---

## 📚 Next Steps

After successful setup:

1. **Upload Test Documents**
   - Upload sample medical documents
   - Verify OCR extraction
   - Check anomaly detection

2. **Try Smart Search**
   - Search for: "What is my HbA1c?"
   - Try: "Show my medications"
   - Test: "Any critical alerts?"

3. **Explore Dashboards**
   - Patient dashboard
   - Upload interface
   - Timeline view
   - Search page

4. **Customize Agents**
   - Edit prompts in `ai_pipelines/`
   - Adjust temperature settings
   - Modify search weights

5. **Deploy to Production**
   - See [DEPLOYMENT.md](docs/DEPLOYMENT.md)
   - Configure HTTPS
   - Set up monitoring

---

## 📞 Support

### Getting Help

- 📖 **Documentation**: Check [README.md](README.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/medivault/issues)
- 💬 **Discord**: [Join Community](https://discord.gg/medivault)
- 📧 **Email**: support@medivault.com

### Useful Commands

```bash
# Check backend status
curl http://localhost:5000/api/agents/health

# View backend logs
tail -f data/logs/medivault.log

# Restart services
# Press Ctrl+C in each terminal, then restart

# Run tests
pytest backend/tests/
cd frontend && npm test
```

---

## ✅ Setup Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Google API key obtained
- [ ] Supabase account created
- [ ] Repository cloned
- [ ] `.env` file configured
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Database migrated
- [ ] Backend running (port 5000)
- [ ] Frontend running (port 5173)
- [ ] Health check passes
- [ ] Test upload successful

---

## 🎉 You're All Set!

MediVault is now running! Start uploading documents and exploring the AI-powered features.

**Quick Test:**
1. Go to `http://localhost:5173`
2. Click "Upload" and select a medical document
3. Wait for processing (5-10 seconds)
4. Go to "Search" and ask: "What did I upload?"

---

**Happy Building! 🚀**

For detailed API documentation, see [API_REFERENCE.md](docs/API_REFERENCE.md)
