import re
from typing import Dict, List
from datetime import datetime

class PrescriptionParser:
    """Parse Indian prescription formats"""

    def __init__(self):
        # Indian prescription abbreviations
        self.frequency_map = {
            'OD': 'once daily',
            'BD': 'twice daily',
            'TDS': 'three times daily',
            'QID': 'four times daily',
            'SOS': 'as needed',
            'STAT': 'immediately',
            'HS': 'at bedtime',
            'AC': 'before meals',
            'PC': 'after meals',
            'PRN': 'as needed'
        }

        self.route_map = {
            'PO': 'oral',
            'IV': 'intravenous',
            'IM': 'intramuscular',
            'SC': 'subcutaneous',
            'SL': 'sublingual',
            'TOP': 'topical'
        }

    def parse_dosage_format(self, dosage_str: str) -> Dict:
        """Parse Indian dosage format (e.g., 1+0+1, 1+1+0)"""
        # Pattern: number+number+number (morning+afternoon+night)
        pattern = r'(\d+)\s*\+\s*(\d+)\s*\+\s*(\d+)'
        match = re.search(pattern, dosage_str)

        if match:
            morning, afternoon, night = map(int, match.groups())
            total_daily = morning + afternoon + night

            return {
                'morning': morning,
                'afternoon': afternoon,
                'night': night,
                'total_daily_doses': total_daily,
                'format': 'indian_plus_notation'
            }

        return None

    def parse_prescription_line(self, line: str) -> Dict:
        """Parse a single prescription line"""
        # Example: "Tab Metformin 500mg 1+0+1 AC x 30 days"

        result = {
            'medication': None,
            'dosage': None,
            'frequency': None,
            'route': 'oral',  # default
            'duration': None,
            'instructions': None
        }

        # Extract medication name and strength
        med_pattern = r'(?:Tab|Cap|Syr|Inj)\.?\s+([A-Za-z\s]+?)(?:\s+(\d+\.?\d*)\s*(mg|g|ml|mcg))?'
        med_match = re.search(med_pattern, line, re.IGNORECASE)
        if med_match:
            result['medication'] = med_match.group(1).strip()
            if med_match.group(2):
                result['dosage'] = f"{med_match.group(2)} {med_match.group(3)}"

        # Extract Indian format dosage
        dosage_format = self.parse_dosage_format(line)
        if dosage_format:
            result['frequency'] = dosage_format

        # Extract standard frequency abbreviations
        for abbr, meaning in self.frequency_map.items():
            if abbr in line.upper():
                if result['frequency'] is None:
                    result['frequency'] = meaning
                else:
                    result['instructions'] = meaning

        # Extract duration
        duration_pattern = r'(?:x|for)\s+(\d+)\s*(days?|weeks?|months?)'
        duration_match = re.search(duration_pattern, line, re.IGNORECASE)
        if duration_match:
            result['duration'] = f"{duration_match.group(1)} {duration_match.group(2)}"

        return result

    def parse_prescription(self, text: str) -> List[Dict]:
        """Parse complete prescription"""
        lines = text.split('\n')
        medications = []

        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue

            # Check if line contains medication indicators
            if re.search(r'(?:Tab|Cap|Syr|Inj)\.?', line, re.IGNORECASE):
                parsed = self.parse_prescription_line(line)
                if parsed['medication']:
                    medications.append(parsed)

        return medications
