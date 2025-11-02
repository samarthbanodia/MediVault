# MediSense: AI-Powered Healthcare Assistant

**MediSense** is an intelligent platform designed to assist both patients and doctors by leveraging state-of-the-art AI to analyze and manage medical records. It provides a seamless interface for uploading medical documents, extracting vital information, and offering smart search and analysis capabilities.

## Key Features

- **Intelligent Document Processing**: Upload medical records (prescriptions, lab reports, etc.) in various formats (PDF, images). Our multi-engine OCR (Tesseract + EasyOCR) with multilingual support ensures accurate data extraction.
- **Smart Search**: A powerful hybrid search engine (semantic + keyword) allows you to find relevant information across all your medical documents.
- **7-Layer Anomaly Detection**: A sophisticated clinical decision support system that flags potential issues in medical reports, providing an extra layer of safety.
- **Patient & Doctor Dashboards**: Separate, intuitive dashboards for patients and doctors to manage and visualize medical data.
- **Secure & Scalable**: Built with a robust backend and a modern frontend, ensuring your data is secure and the platform is scalable.

## Architecture Overview

<img width="1151" height="418" alt="image" src="https://github.com/user-attachments/assets/13170edc-64a1-4bd8-8be3-dd29831d9940" />

<img width="1128" height="211" alt="image" src="https://github.com/user-attachments/assets/c64c3a04-6a85-46db-b5a6-fcd546165827" />


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

## Project Structure

```
MediSense/
├── frontend_figma/         # React frontend application
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Application pages
│   │   └── ...
│   ├── package.json
│   └── ...
├── pipelines/              # AI pipelines
│   ├── components/         # Pipeline components (OCR, NER, etc.)
│   ├── ingestion.py        # Document ingestion pipeline
│   └── search.py           # Search pipeline
├── api/                    # Backend API endpoints
├── data/                   # Data files (biomarker ranges, etc.)
├── tests/                  # Test scripts
├── app.py                  # Main backend application file
├── requirements.txt        # Python dependencies
└── README.md
```

## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
<img width="1128" height="211" alt="image" src="https://github.com/user-attachments/assets/f1e68b22-9cff-4e5a-9b80-c080e63e07b3" />
