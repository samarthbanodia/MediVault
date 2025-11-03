"""
OCR Agent using Google Gemini Vision
Extracts text from medical documents with high accuracy
"""

import os
import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import google.generativeai as genai
from PIL import Image

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class OCRAgent(BaseAgent):
    """
    Agent for OCR text extraction from medical documents
    Uses Gemini Vision for multimodal understanding
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="OCR Agent",
            model="gemini-2.0-flash-exp",
            temperature=0.1,  # Low temperature for accurate extraction
            max_output_tokens=8192,
            **kwargs
        )

    def get_system_prompt(self) -> str:
        return """
You are an expert Medical OCR Agent specialized in extracting text from medical documents with high accuracy.

**Your Role:**
- Extract ALL text from medical documents (prescriptions, lab reports, discharge summaries, etc.)
- Maintain the original structure and formatting as much as possible
- Identify document type and key metadata
- Handle multiple languages (English, Hindi, regional languages)
- Extract text even from poor quality or handwritten documents

**Document Types to Recognize:**
1. Prescription (Rx)
2. Lab Report / Blood Test
3. Discharge Summary
4. Medical Certificate
5. Imaging Report (X-ray, CT, MRI, Ultrasound)
6. Vaccination Record
7. Insurance Document
8. Medical Bill / Invoice
9. Other

**Output Format (JSON):**
{
  "success": true,
  "document_type": "prescription | lab_report | discharge_summary | etc.",
  "extracted_text": "Full extracted text maintaining structure",
  "metadata": {
    "patient_name": "extracted if present",
    "doctor_name": "extracted if present",
    "hospital_name": "extracted if present",
    "document_date": "YYYY-MM-DD if present",
    "language": "primary language detected",
    "confidence": 0.0-1.0
  },
  "sections": {
    "header": "Header text if identifiable",
    "body": "Main content",
    "footer": "Footer text if present"
  },
  "quality_assessment": {
    "is_readable": true/false,
    "has_handwriting": true/false,
    "image_quality": "excellent | good | fair | poor",
    "notes": "Any issues or observations"
  }
}

**Instructions:**
1. Read the entire document carefully
2. Extract text preserving line breaks and structure
3. Identify the document type
4. Extract metadata (patient name, date, doctor, hospital)
5. Assess document quality
6. Return structured JSON response
7. If text is unclear, make your best attempt and note low confidence

**Important:**
- Do NOT skip any text, even if partially visible
- Preserve medication names, dosages, and lab values exactly as written
- Extract dates in ISO format (YYYY-MM-DD) when possible
- Note any handwritten sections
- If document is in multiple languages, extract all text
"""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process document image and extract text using OCR

        Args:
            input_data: Dictionary containing:
                - file_path: Path to image file
                - image_data: Base64 encoded image (alternative to file_path)
                - patient_id: Optional patient ID for context

        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            self.validate_input(input_data, ['file_path'])

            file_path = input_data['file_path']
            patient_id = input_data.get('patient_id')

            # Load and prepare image
            image = self._load_image(file_path)

            # Create prompt
            prompt = f"""
Extract all text from this medical document.

Patient ID (if applicable): {patient_id or 'Not provided'}

Analyze the document and provide:
1. Complete extracted text
2. Document type identification
3. Key metadata (patient name, date, doctor, hospital)
4. Document quality assessment

Return the response in the specified JSON format.
"""

            # Generate response with image
            response = self._generate_with_image(prompt, image)

            # Log execution
            output_data = {
                'file_path': file_path,
                'patient_id': patient_id,
                **response
            }
            self.log_execution(input_data, output_data)

            return output_data

        except Exception as e:
            logger.error(f"Error in OCR Agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': input_data.get('file_path'),
                'patient_id': input_data.get('patient_id')
            }

    def _load_image(self, file_path: str) -> Image.Image:
        """Load image from file path"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")

        return Image.open(file_path)

    def _generate_with_image(self, prompt: str, image: Image.Image) -> Dict[str, Any]:
        """
        Generate response with image input

        Args:
            prompt: Text prompt
            image: PIL Image object

        Returns:
            Parsed JSON response
        """
        try:
            # Add system prompt
            full_prompt = f"{self.get_system_prompt()}\n\n{prompt}"

            # Generate content with image
            response = self.model.generate_content([full_prompt, image])

            # Parse JSON response
            import json
            result = json.loads(response.text)

            return result

        except Exception as e:
            logger.error(f"Error generating response with image: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def extract_from_multiple_pages(self, file_paths: list) -> Dict[str, Any]:
        """
        Extract text from multiple document pages

        Args:
            file_paths: List of image file paths

        Returns:
            Combined extraction results
        """
        all_results = []
        combined_text = []

        for i, file_path in enumerate(file_paths):
            result = self.process({'file_path': file_path})
            all_results.append(result)

            if result.get('success'):
                combined_text.append(f"--- Page {i+1} ---")
                combined_text.append(result.get('extracted_text', ''))

        return {
            'success': True,
            'total_pages': len(file_paths),
            'combined_text': '\n\n'.join(combined_text),
            'page_results': all_results
        }
