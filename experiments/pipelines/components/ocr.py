import easyocr
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from typing import Dict, List
import os
import logging

logger = logging.getLogger(__name__)

class MedicalOCR:
    """Multi-engine OCR for medical documents with robust PDF support"""

    def __init__(self):
        # Initialize EasyOCR (supports Hindi + English)
        self.easy_reader = easyocr.Reader(['en', 'hi'], gpu=False)
        logger.info("MedicalOCR initialized with EasyOCR (English + Hindi)")

    def extract_text_from_pdf_direct(self, pdf_path: str) -> Dict:
        """
        Try to extract text directly from PDF (fast method for text-based PDFs)

        Returns:
            Dict with 'text', 'confidence', 'method'
        """
        try:
            doc = fitz.open(pdf_path)
            text_parts = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)

            doc.close()

            combined_text = '\n\n--- Page Break ---\n\n'.join(text_parts)

            # If we got substantial text, return it
            if combined_text.strip() and len(combined_text.strip()) > 50:
                logger.info(f"Extracted {len(combined_text)} chars directly from PDF ({len(text_parts)} pages)")
                return {
                    'text': combined_text,
                    'confidence': 95.0,  # High confidence for direct extraction
                    'method': 'pdf_direct',
                    'num_pages': len(text_parts)
                }
            else:
                logger.info("PDF has minimal text, will use OCR")
                return None

        except Exception as e:
            logger.error(f"Error extracting text directly from PDF: {e}")
            return None

    def pdf_pages_to_images(self, pdf_path: str, dpi: int = 300) -> List[np.ndarray]:
        """
        Convert PDF pages to images for OCR

        Args:
            pdf_path: Path to PDF file
            dpi: Resolution (higher = better quality but slower)

        Returns:
            List of numpy arrays (images)
        """
        try:
            doc = fitz.open(pdf_path)
            images = []

            for page_num in range(len(doc)):
                page = doc[page_num]

                # Render page to pixmap at specified DPI
                mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72 is default PDF DPI
                pix = page.get_pixmap(matrix=mat)

                # Convert pixmap to numpy array
                img_data = pix.samples
                img = np.frombuffer(img_data, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

                # Convert RGBA to RGB if needed
                if pix.n == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                elif pix.n == 1:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

                # Convert RGB to BGR for OpenCV
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                images.append(img)

            doc.close()
            logger.info(f"Converted PDF to {len(images)} images at {dpi} DPI")
            return images

        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []

    def load_image(self, image_path: str) -> List[np.ndarray]:
        """Load regular image file"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to load image: {image_path}")
                return []
            return [img]
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return []

    def extract_text_easyocr(self, img: np.ndarray) -> Dict:
        """Extract text using EasyOCR from a single image"""
        try:
            # Use EasyOCR
            results = self.easy_reader.readtext(img)

            # Combine all text and calculate average confidence
            text_parts = []
            confidences = []

            for (bbox, text, conf) in results:
                text_parts.append(text)
                confidences.append(conf)

            full_text = '\n'.join(text_parts)
            avg_confidence = (sum(confidences) / len(confidences) * 100) if confidences else 0

            return {
                'text': full_text,
                'confidence': avg_confidence,
                'method': 'easyocr',
                'num_detections': len(results)
            }
        except Exception as e:
            logger.error(f"Error in EasyOCR extraction: {e}")
            return {
                'text': '',
                'confidence': 0,
                'method': 'easyocr',
                'error': str(e)
            }

    def extract_text(self, file_path: str) -> Dict:
        """
        Main OCR method with intelligent PDF handling

        Process:
        1. For PDFs: Try direct text extraction first (fast)
        2. If that fails: Convert to images and use OCR
        3. For images: Use OCR directly

        Args:
            file_path: Path to PDF or image file

        Returns:
            Dict with 'text', 'confidence', 'method', and optional metadata
        """
        try:
            logger.info(f"Starting OCR for: {file_path}")

            file_ext = os.path.splitext(file_path)[1].lower()

            # Handle PDFs
            if file_ext == '.pdf':
                # Try direct text extraction first (fast for text-based PDFs)
                direct_result = self.extract_text_from_pdf_direct(file_path)

                if direct_result and direct_result['text'].strip():
                    logger.info("PDF text extracted directly (no OCR needed)")
                    return direct_result

                # Fall back to OCR if direct extraction failed
                logger.info("Converting PDF to images for OCR...")
                images = self.pdf_pages_to_images(file_path, dpi=300)

                if not images:
                    return {
                        'text': '',
                        'confidence': 0,
                        'method': 'failed',
                        'error': 'Could not process PDF'
                    }
            else:
                # Load regular image
                images = self.load_image(file_path)

                if not images:
                    return {
                        'text': '',
                        'confidence': 0,
                        'method': 'failed',
                        'error': 'Could not load image'
                    }

            # Process all images with OCR
            all_text = []
            all_confidences = []

            for idx, img in enumerate(images):
                logger.info(f"Processing page/image {idx+1}/{len(images)} with EasyOCR...")
                result = self.extract_text_easyocr(img)

                if result['text']:
                    all_text.append(result['text'])
                    all_confidences.append(result['confidence'])

            # Combine results
            if not all_text:
                logger.warning("No text extracted from any page")
                return {
                    'text': '',
                    'confidence': 0,
                    'method': 'easyocr',
                    'num_pages': len(images)
                }

            combined_text = '\n\n--- Page Break ---\n\n'.join(all_text)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0

            logger.info(f"OCR complete: {len(combined_text)} chars, confidence: {avg_confidence:.2f}%")

            return {
                'text': combined_text,
                'confidence': avg_confidence,
                'method': 'easyocr_on_images',
                'num_pages': len(images)
            }

        except Exception as e:
            logger.error(f"Error in extract_text: {e}")
            import traceback
            traceback.print_exc()
            return {
                'text': '',
                'confidence': 0,
                'method': 'failed',
                'error': str(e)
            }
