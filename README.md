# MediSense: AI-Powered Healthcare Assistant

**MediSense** is an intelligent platform designed to assist both patients and doctors by leveraging state-of-the-art AI to analyze and manage medical records. It provides a seamless interface for uploading medical documents, extracting vital information, and offering smart search and analysis capabilities.

## Key Features

- **Intelligent Document Processing**: Upload medical records (prescriptions, lab reports, etc.) in various formats (PDF, images). Our multi-engine OCR (Tesseract + EasyOCR) with multilingual support ensures accurate data extraction.
- **Smart Search**: A powerful hybrid search engine (semantic + keyword) allows you to find relevant information across all your medical documents.
- **7-Layer Anomaly Detection**: A sophisticated clinical decision support system that flags potential issues in medical reports, providing an extra layer of safety.
- **Patient & Doctor Dashboards**: Separate, intuitive dashboards for patients and doctors to manage and visualize medical data.
- **Secure & Scalable**: Built with a robust backend and a modern frontend, ensuring your data is secure and the platform is scalable.

## Architecture Overview

<img width="1151" height="418" alt="image" src="https://github.com/user-attachments/assets/6a7aa704-26e9-4f24-be8f-1c04051b7b2e" />


<img width="1128" height="211" alt="image" src="https://github.com/user-attachments/assets/8fd0c66b-34b1-4d0f-b617-e88e644e2d88" />



MediSense is built with a modern, decoupled architecture:

- **Frontend**: A React-based single-page application (SPA) built with Vite and TypeScript, using ShadCN UI for a clean and modern user interface.
- **Backend**: A Python-based backend powered by Flask, responsible for handling API requests, processing documents, and managing the database.
- **AI Pipeline**: A set of Python scripts that form the core of our AI-powered features, including OCR, NER, anomaly detection, and search.
- **Database**: A combination of a relational database (SQLite) for storing structured data and a vector database (ChromaDB) for enabling semantic search.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Tesseract OCR**:
    - **Windows**: Download and install from [UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki). Add the installation directory (e.g., `C:\Program Files\Tesseract-OCR`) to your system's PATH.
    - **macOS**: `brew install tesseract`
    - **Linux**: `sudo apt-get install tesseract-ocr`

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/MediSense.git
    cd MediSense
    ```

2.  **Backend Setup:**

    ```bash
    # Create and activate a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    # Install Python dependencies
    pip install -r requirements.txt

    # Download spaCy model
    python -m spacy download en_core_web_sm
    ```

3.  **Frontend Setup:**

    ```bash
    # Navigate to the frontend directory
    cd frontend_figma

    # Install npm dependencies
    npm install
    ```

### Running the Application

1.  **Start the Backend Server:**

    ```bash
    # From the root directory
    python app.py
    ```

2.  **Start the Frontend Development Server:**

    ```bash
    # From the frontend_figma directory
    npm run dev
    ```

3.  **Access the Application:**

    Open your browser and navigate to `http://localhost:5173`.

## 🚀 Key Features

### 1. Document Ingestion Pipeline
```
Image Upload → OCR → Medical NER → Prescription Parsing
→ 7-Layer Anomaly Detection → Embeddings → Vector DB Storage
```

**Capabilities:**
- Multi-language OCR (English + Hindi)
- Automatic fallback between OCR engines
- Medical entity extraction (diseases, medications, biomarkers)
- Indian prescription format support (1+0+1)
- Clinical severity scoring (0-100)
- Automatic vector embedding and storage

### 2. Smart Search Pipeline
```
User Query → Intent Parsing → Semantic Search
→ Keyword Filtering → Hybrid Ranking → Results
```

**Capabilities:**
- Natural language queries
- Multilingual support
- Temporal filtering ("last week", "last month")
- Biomarker-specific searches
- Condition-based filtering
- Patient-specific queries

### 3. 7-Layer Anomaly Detection

1. **Layer 1:** Range check against normal values
2. **Layer 2:** Critical value detection (emergency alerts)
3. **Layer 3:** Age-adjusted reference ranges
4. **Layer 4:** Medication context analysis
5. **Layer 5:** Comorbidity pattern detection
6. **Layer 6:** Trend analysis vs historical data
7. **Layer 7:** Drug-drug interaction checking

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **OCR** | Tesseract 5.x | Fast printed text |
| **OCR** | EasyOCR | Handwritten text, Hindi |
| **NER** | HuggingFace Transformers | Medical entity extraction |
| **Embeddings** | Sentence Transformers | Semantic search |
| **Vector DB** | ChromaDB | Fast similarity search |
| **NLP** | spaCy | Query parsing |
| **Framework** | PyTorch | Deep learning backend |

---

## 📦 Models Used

### 1. Medical NER
- **Model:** `blaze999/Medical-NER`
- **Size:** 420MB
- **Accuracy:** 85-90%
- **Purpose:** Extract diseases, medications, symptoms

### 2. Embeddings
- **Model:** `paraphrase-multilingual-mpnet-base-v2`
- **Size:** 1.1GB
- **Dimensions:** 768
- **Purpose:** Multilingual semantic search
- **Alternative:** `all-MiniLM-L6-v2` (80MB, faster)

### 3. OCR
- **Tesseract:** Pre-installed, fast, good for printed text
- **EasyOCR:** Auto-download, good for handwritten text

### 4. NLP
- **spaCy:** `en_core_web_sm` (13MB) for query parsing

---

## 🎯 What Can Be Done Now

### Immediate Capabilities

1. **Process Medical Documents:**
   ```python
   pipeline = IngestionPipeline()
   result = pipeline.process_document('prescription.jpg', patient_info)
   ```

2. **Search Medical Records:**
   ```python
   search = SearchPipeline()
   results = search.search("diabetes patients with high glucose")
   ```

3. **Detect Anomalies:**
   ```python
   detector = AnomalyDetector()
   anomalies = detector.detect_anomalies(medical_record)
   ```

4. **Parse Prescriptions:**
   ```python
   parser = PrescriptionParser()
   prescriptions = parser.parse_prescription(text)
   ```

---
