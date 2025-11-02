import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipelines.components.ner import MedicalNER
from pipelines.components.prescription_parser import PrescriptionParser
from pipelines.components.anomaly_detector import AnomalyDetector
from pipelines.components.embeddings import MedicalEmbeddings


class TestNER(unittest.TestCase):
    """Test Medical NER component"""

    def setUp(self):
        self.ner = MedicalNER()

    def test_extract_entities(self):
        """Test entity extraction"""
        text = "Patient diagnosed with Type 2 Diabetes. Prescribed Metformin 500mg."
        entities = self.ner.extract_entities(text)

        self.assertIsInstance(entities, dict)
        self.assertIn('diseases', entities)
        self.assertIn('medications', entities)

    def test_biomarker_values(self):
        """Test biomarker value extraction"""
        text = "Glucose: 180 mg/dL, BP: 140/90, HbA1c: 8.5%"
        biomarkers = self.ner.extract_biomarker_values(text)

        self.assertIsInstance(biomarkers, list)
        self.assertGreater(len(biomarkers), 0)


class TestPrescriptionParser(unittest.TestCase):
    """Test Prescription Parser"""

    def setUp(self):
        self.parser = PrescriptionParser()

    def test_dosage_format(self):
        """Test Indian dosage format parsing"""
        result = self.parser.parse_dosage_format("1+0+1")

        self.assertIsNotNone(result)
        self.assertEqual(result['morning'], 1)
        self.assertEqual(result['afternoon'], 0)
        self.assertEqual(result['night'], 1)
        self.assertEqual(result['total_daily_doses'], 2)

    def test_prescription_line(self):
        """Test prescription line parsing"""
        line = "Tab Metformin 500mg 1+0+1 AC x 30 days"
        result = self.parser.parse_prescription_line(line)

        self.assertEqual(result['medication'], 'Metformin')
        self.assertEqual(result['dosage'], '500 mg')
        self.assertIsNotNone(result['frequency'])

    def test_full_prescription(self):
        """Test full prescription parsing"""
        text = """
        Tab Metformin 500mg 1+0+1 AC x 30 days
        Tab Amlodipine 5mg 1+0+0 x 30 days
        """
        prescriptions = self.parser.parse_prescription(text)

        self.assertEqual(len(prescriptions), 2)


class TestAnomalyDetector(unittest.TestCase):
    """Test Anomaly Detector"""

    def setUp(self):
        self.detector = AnomalyDetector(data_dir='./data')

    def test_range_check(self):
        """Test biomarker range checking"""
        biomarker = {'type': 'glucose', 'value': 250}
        result = self.detector.layer1_range_check(biomarker)

        self.assertTrue(result.get('anomaly', False))

    def test_critical_check(self):
        """Test critical value detection"""
        biomarker = {'type': 'glucose', 'value': 350}
        result = self.detector.layer2_critical_check(biomarker)

        self.assertTrue(result.get('critical', False))

    def test_full_detection(self):
        """Test complete anomaly detection"""
        record = {
            'patient_age': 45,
            'biomarkers': [
                {'type': 'glucose', 'value': 250, 'unit': 'mg/dL'}
            ],
            'medications': [{'medication': 'Metformin'}],
            'diseases': [{'text': 'diabetes'}]
        }

        results = self.detector.detect_anomalies(record)

        self.assertIn('overall_severity', results)
        self.assertIn('anomalies', results)
        self.assertGreater(results['overall_severity'], 0)


class TestEmbeddings(unittest.TestCase):
    """Test Embeddings component"""

    def setUp(self):
        # Use smaller model for testing
        self.embeddings = MedicalEmbeddings(model_name='all-MiniLM-L6-v2')

    def test_create_medical_text(self):
        """Test medical record text creation"""
        record = {
            'patient_id': 'TEST001',
            'diseases': [{'text': 'diabetes'}],
            'medications': [{'medication': 'Metformin'}],
            'biomarkers': [{'type': 'glucose', 'value': 120}]
        }

        text = self.embeddings.create_medical_record_text(record)

        self.assertIsInstance(text, str)
        self.assertIn('TEST001', text)

    def test_embed_record(self):
        """Test embedding generation"""
        record = {
            'patient_id': 'TEST001',
            'diseases': [{'text': 'diabetes'}],
            'medications': [{'medication': 'Metformin'}],
            'biomarkers': [{'type': 'glucose', 'value': 120}]
        }

        embedding = self.embeddings.embed_record(record)

        self.assertEqual(len(embedding.shape), 1)
        self.assertEqual(embedding.shape[0], self.embeddings.dimension)

    def test_similarity(self):
        """Test similarity calculation"""
        record1 = {
            'patient_id': 'TEST001',
            'diseases': [{'text': 'diabetes'}],
        }
        record2 = {
            'patient_id': 'TEST002',
            'diseases': [{'text': 'diabetes'}],
        }

        emb1 = self.embeddings.embed_record(record1)
        emb2 = self.embeddings.embed_record(record2)

        similarity = self.embeddings.similarity(emb1, emb2)

        self.assertGreater(similarity, 0.5)  # Should be similar


if __name__ == '__main__':
    unittest.main()
