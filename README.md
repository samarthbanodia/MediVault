# 🏥 MediVault - AI-Powered Medical Records Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini%202.0-orange.svg)](https://ai.google.dev/)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Transform scattered medical documents into intelligent, searchable health insights using Google's Gemini AI**

MediVault is a cutting-edge healthcare platform that leverages **Google ADK (Agentic Development Kit)** with Gemini 2.0 Flash to provide intelligent medical document processing, semantic search, and AI-powered health insights.

---

## 🌟 Key Features

### 🤖 Multi-Agent AI System
- **8 Specialized AI Agents** powered by Google Gemini
- **OCR Agent** - Extract text from any medical document
- **Medical NER Agent** - Identify diseases, medications, biomarkers
- **Prescription Parser** - Parse Indian prescription formats
- **7-Layer Anomaly Detection** - Comprehensive health risk assessment
- **Smart Search** - Semantic + keyword hybrid search
- **AI Analyser** - Generate evidence-based health insights

### 🔍 Intelligent Features
- 📄 **Multi-format Document Processing** (PDF, JPG, PNG, TIFF)
- 🌐 **Multi-language Support** (English, Hindi, regional languages)
- 🔬 **Advanced Medical NER** (7 entity categories)
- ⚠️ **Real-time Anomaly Detection** (7-layer system)
- 🔎 **Semantic Search** across all medical records
- 📊 **Trend Analysis** and health timeline visualization
- 💊 **Drug Interaction Checking**
- 📱 **Patient & Doctor Dashboards**

### 🎯 Use Cases
- 📂 Organize scattered medical documents
- 🔍 Quick search: "What is my latest HbA1c?"
- 📈 Track biomarker trends over time
- ⚕️ Clinical decision support for doctors
- 🚨 Automated critical alert detection
- 💬 Natural language health Q&A

---

## 🏗️ Architecture

MediVault implements a **sophisticated multi-agent architecture** with two main workflows:

### 1️⃣ Patient Flow (Document Processing)
```
Upload → OCR Agent → Medical NER → Prescription Parser
   → 7-Layer Anomaly Detection → Normalizer → Embedding → Vector DB
```

### 2️⃣ Smart Search Flow
```
Query → Embedding → Semantic Search → Top K Results
   → AI Analyser → Evidence-Based Response
```

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                        │
│          Dashboard | Upload | Search | Timeline             │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────────┐
│                  Backend (Flask + Agents)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Agent Orchestrator (Coordinator)             │  │
│  └─────┬────────────────────────────────────────┬───────┘  │
│        │                                        │           │
│  ┌─────▼─────┐  ┌────────┐  ┌─────────┐  ┌────▼──────┐   │
│  │OCR Agent  │  │NER     │  │Anomaly  │  │Search     │   │
│  │           │→ │Agent   │→ │Detector │  │Agent      │   │
│  └───────────┘  └────────┘  └─────────┘  └───────────┘   │
│                                                            │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │Prescription │  │Normalizer    │  │AI Analyser      │ │
│  │Parser       │→ │Agent         │→ │Agent            │ │
│  └─────────────┘  └──────────────┘  └─────────────────┘ │
└──────────────┬─────────────────────────────┬──────────────┘
               │                             │
         ┌─────▼──────┐              ┌──────▼──────┐
         │  Supabase  │              │  ChromaDB   │
         │(PostgreSQL)│              │  (Vectors)  │
         └────────────┘              └─────────────┘
```

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [AI Pipelines](#-ai-pipelines)
- [Frontend](#-frontend)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google API Key ([Get it here](https://makersuite.google.com/app/apikey))
- Supabase Account ([Sign up](https://supabase.com))

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/medivault.git
cd medivault

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Configure environment
cp config/.env.example .env
# Edit .env with your API keys

# 5. Run backend
python backend/app.py

# 6. Run frontend (in another terminal)
cd frontend && npm run dev

# ✅ Access at http://localhost:5173
```

---

## 💻 Installation

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Build for production (optional)
npm run build
```

### AI Pipelines Setup

```bash
# AI pipelines are automatically loaded by backend
# Ensure dependencies are installed
pip install -r ai_pipelines/requirements.txt
```

---

## ⚙️ Configuration

### 1. Environment Variables

Create `.env` file in root directory:

```env
# Google Gemini Configuration (Required)
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-2.0-flash-exp
EMBEDDING_MODEL=text-embedding-004

# Supabase Configuration (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Vector Database
VECTOR_DB_PATH=./data/chroma_db
VECTOR_DB_COLLECTION=medical_records

# Server Configuration
FLASK_PORT=5000
FRONTEND_PORT=5173
FLASK_DEBUG=False

# File Upload
UPLOAD_FOLDER=./data/uploads
MAX_FILE_SIZE_MB=16

# Security
JWT_SECRET_KEY=your-secure-random-string-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Logging
LOG_LEVEL=INFO
LOG_FILE=./data/logs/medivault.log
```

### 2. Google API Key Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy and add to `.env` file

### 3. Supabase Setup

1. Create account at [Supabase](https://supabase.com)
2. Create new project
3. Get API keys from Settings → API
4. Run database migrations:

```bash
cd backend
python scripts/setup_database.py
```

---

## 📖 Usage

### Upload Medical Document

```bash
curl -X POST http://localhost:5000/api/agents/upload \
  -F "file=@lab_report.pdf" \
  -F "patient_id=patient-123" \
  -F "patient_metadata={\"age\":45,\"gender\":\"M\"}"
```

### Smart Search Query

```bash
curl -X POST http://localhost:5000/api/agents/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is my current HbA1c level?",
    "patient_id": "patient-123"
  }'
```

### Python SDK

```python
from ai_pipelines.orchestrator import AgentOrchestrator

# Initialize
orchestrator = AgentOrchestrator()

# Upload document
result = orchestrator.process_patient_document(
    file_path='lab_report.pdf',
    patient_id='patient-123',
    patient_metadata={'age': 45, 'gender': 'M'}
)

print(f"Severity: {result['overall_severity']}/100")
print(f"Critical Alerts: {result['has_critical_alerts']}")

# Smart search
search_result = orchestrator.smart_search(
    query='What is my HbA1c?',
    patient_id='patient-123'
)

print(f"Answer: {search_result['response']}")
```

---

## 🔌 API Documentation

### Core Endpoints

#### Upload Document
```http
POST /api/agents/upload
Content-Type: multipart/form-data

Parameters:
  - file: Medical document (PDF/Image)
  - patient_id: Patient identifier
  - patient_metadata: JSON with patient info (optional)

Response:
{
  "success": true,
  "record_id": "REC_20240115_123456",
  "document_type": "lab_report",
  "has_critical_alerts": false,
  "overall_severity": 25,
  "clinical_summary": {...}
}
```

#### Smart Search
```http
POST /api/agents/search
Content-Type: application/json

Body:
{
  "query": "diabetes medications",
  "patient_id": "patient-123",
  "top_k": 5
}

Response:
{
  "success": true,
  "ranked_results": [...]
}
```

#### Ask Question (AI Analysis)
```http
POST /api/agents/ask
Content-Type: application/json

Body:
{
  "query": "What is my HbA1c?",
  "patient_id": "patient-123"
}

Response:
{
  "success": true,
  "response": "Your most recent HbA1c is 7.2%...",
  "evidence": [...],
  "recommendations": [...],
  "confidence_score": 0.92
}
```

#### Patient Summary
```http
GET /api/agents/patient/{patient_id}/summary

Response:
{
  "success": true,
  "answer": "Comprehensive health summary...",
  "key_findings": [...],
  "areas_of_concern": [...]
}
```

#### Critical Alerts
```http
GET /api/agents/patient/{patient_id}/alerts
GET /api/agents/alerts  # All patients

Response:
{
  "success": true,
  "total_alerts": 3,
  "alerts": [...]
}
```

See [API_REFERENCE.md](docs/API_REFERENCE.md) for complete documentation.

---

## 🤖 AI Pipelines

MediVault uses **8 specialized AI agents** for medical intelligence:

### Agent Overview

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| **OCR Agent** | Text extraction | Document image | Extracted text + metadata |
| **Medical NER** | Entity extraction | Text | Diseases, meds, biomarkers |
| **Prescription Parser** | Parse Rx formats | Prescription text | Structured medication data |
| **Anomaly Detector** | 7-layer detection | Medical data | Severity score + alerts |
| **Normalizer** | Standardization | Raw entities | ICD-10, LOINC codes |
| **Embedding Agent** | Vector creation | Text | 768-d embeddings |
| **Search Agent** | Hybrid search | Query | Ranked results |
| **AI Analyser** | Response generation | Search results | Evidence-based answer |

### 7-Layer Anomaly Detection

1. **Layer 1**: Range Check - Compare against normal values
2. **Layer 2**: Critical Values - Life-threatening thresholds
3. **Layer 3**: Age-Adjusted - Age-specific ranges
4. **Layer 4**: Medication Context - Drug interactions
5. **Layer 5**: Trend Analysis - Historical comparison
6. **Layer 6**: Comorbidity Patterns - Disease combinations
7. **Layer 7**: Risk Scoring - Overall risk (0-100)

### Customizing Agents

Edit agent prompts in `ai_pipelines/`:

```python
# ai_pipelines/ocr_agent.py
class OCRAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """
        You are an expert Medical OCR Agent...
        [Customize instructions here]
        """
```

See [AI_PIPELINES.md](docs/AI_PIPELINES.md) for detailed documentation.

---

## 🎨 Frontend

### Tech Stack
- **React 18.3.1** with TypeScript
- **Vite** for fast builds
- **Tailwind CSS** for styling
- **ShadCN UI** components
- **Recharts** for visualizations
- **Axios** for API calls

### Project Structure

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── Dashboard.tsx
│   │   ├── UploadPage.tsx
│   │   ├── SearchPage.tsx
│   │   └── ui/            # ShadCN UI components
│   ├── contexts/          # React contexts
│   ├── services/          # API clients
│   ├── hooks/             # Custom hooks
│   └── lib/               # Utilities
├── public/
└── package.json
```

### Running Frontend

```bash
cd frontend

# Development
npm run dev

# Production build
npm run build
npm run preview
```

### Customizing UI

```tsx
// src/components/Dashboard.tsx
import { Card } from './ui/card';

export function Dashboard() {
  // Customize dashboard layout
}
```

See [FRONTEND.md](docs/FRONTEND.md) for detailed guide.

---

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:5000
```

### Manual Deployment

#### Backend
```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

#### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder to Vercel/Netlify
```

### Cloud Platforms

- **Backend**: Deploy to Render, Railway, or Google Cloud Run
- **Frontend**: Deploy to Vercel, Netlify, or Cloudflare Pages
- **Database**: Use Supabase (managed PostgreSQL)
- **Vector DB**: Self-host ChromaDB or use hosted solution

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## 📊 Project Statistics

- **8** Specialized AI Agents
- **10,000+** Tokens of prompt engineering
- **7** Layers of anomaly detection
- **50+** React components
- **15+** API endpoints
- **7** Medical entity categories
- **3** Search modes (semantic, keyword, hybrid)

---

## 🔒 Security

- ✅ Environment variable configuration
- ✅ File upload validation
- ✅ Input sanitization
- ✅ JWT authentication
- ✅ SQL injection prevention
- ✅ XSS protection
- ⚠️ Implement HTTPS in production
- ⚠️ Add rate limiting
- ⚠️ Enable CORS properly

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e

# Agent tests
python ai_pipelines/tests/test_agents.py
```

---

## 📈 Performance

- **Document Processing**: 5-10 seconds per document
- **Search Query**: 1-2 seconds
- **AI Analysis**: 2-3 seconds
- **Concurrent Users**: 100+ (with proper scaling)
- **Vector Search**: Sub-second for 100K documents

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/medivault.git
cd medivault

# Create branch
git checkout -b feature/my-feature

# Make changes and test
python -m pytest

# Commit and push
git commit -m "Add my feature"
git push origin feature/my-feature

# Create Pull Request
```

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 👥 Team

Built with ❤️ by the MediVault team

- **Lead Developer**: [Your Name]
- **AI/ML Engineer**: [Name]
- **Frontend Developer**: [Name]

---

## 🙏 Acknowledgments

- **Google Gemini** for powerful AI capabilities
- **Supabase** for database infrastructure
- **ChromaDB** for vector search
- **ShadCN** for UI components
- **React** and **Flask** communities

---

## 📞 Support

- 📧 Email: support@medivault.com
- 💬 Discord: [Join our community](https://discord.gg/medivault)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/medivault/issues)
- 📖 Docs: [Documentation](https://docs.medivault.com)

---

## 🗺️ Roadmap

### Q1 2024
- ✅ Multi-agent system with Google Gemini
- ✅ 7-layer anomaly detection
- ✅ Semantic search
- ✅ Patient & doctor dashboards

### Q2 2024
- 🔄 Mobile app (React Native)
- 🔄 Voice input for queries
- 🔄 Multi-language support expansion
- 🔄 FHIR compliance

### Q3 2024
- 📋 Telemedicine integration
- 📋 Wearable device integration
- 📋 Prescription ordering
- 📋 Insurance claim assistance

### Q4 2024
- 📋 Multi-tenant support
- 📋 Advanced analytics dashboard
- 📋 Blockchain for audit trails
- 📋 International expansion

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/medivault&type=Date)](https://star-history.com/#yourusername/medivault&Date)

---

## 📸 Screenshots

### Patient Dashboard
![Patient Dashboard](docs/screenshots/dashboard.png)

### Smart Search
![Smart Search](docs/screenshots/search.png)

### Document Upload
![Upload](docs/screenshots/upload.png)

### Health Timeline
![Timeline](docs/screenshots/timeline.png)

---

<div align="center">

**[Website](https://medivault.com)** •
**[Documentation](https://docs.medivault.com)** •
**[API Reference](https://api.medivault.com)** •
**[Blog](https://blog.medivault.com)**

Made with ❤️ using Google Gemini 2.0 Flash

</div>
