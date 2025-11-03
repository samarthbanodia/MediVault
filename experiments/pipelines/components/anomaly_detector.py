import json
from typing import Dict, List
from datetime import datetime
import os

class AnomalyDetector:
    """7-layer anomaly detection for medical records"""

    def __init__(self, data_dir: str = './data'):
        # Load reference data
        with open(os.path.join(data_dir, 'biomarker_ranges.json'), 'r') as f:
            self.biomarker_ranges = json.load(f)

        with open(os.path.join(data_dir, 'drug_interactions.json'), 'r') as f:
            self.drug_interactions = json.load(f)

    def layer1_range_check(self, biomarker: Dict) -> Dict:
        """Layer 1: Check if biomarker is within normal range"""
        biomarker_type = biomarker['type']
        value = biomarker['value']

        if biomarker_type not in self.biomarker_ranges:
            return {'anomaly': False, 'reason': 'unknown_biomarker'}

        ranges = self.biomarker_ranges[biomarker_type]
        normal_min = ranges['normal']['min']
        normal_max = ranges['normal']['max']

        if value < normal_min:
            severity = self._calculate_severity(value, normal_min, ranges.get('critical_low', 0))
            return {
                'anomaly': True,
                'type': 'below_range',
                'severity': severity,
                'message': f'{biomarker_type} is low ({value})'
            }
        elif value > normal_max:
            severity = self._calculate_severity(value, normal_max, ranges.get('critical_high', 1000))
            return {
                'anomaly': True,
                'type': 'above_range',
                'severity': severity,
                'message': f'{biomarker_type} is high ({value})'
            }

        return {'anomaly': False}

    def layer2_critical_check(self, biomarker: Dict) -> Dict:
        """Layer 2: Check for critical values requiring immediate action"""
        biomarker_type = biomarker['type']
        value = biomarker['value']

        if biomarker_type not in self.biomarker_ranges:
            return {'critical': False}

        ranges = self.biomarker_ranges[biomarker_type]

        if 'critical_low' in ranges and value < ranges['critical_low']:
            return {
                'critical': True,
                'severity': 100,
                'message': f'CRITICAL: {biomarker_type} dangerously low ({value})',
                'recommendation': 'Immediate medical attention required'
            }
        elif 'critical_high' in ranges and value > ranges['critical_high']:
            return {
                'critical': True,
                'severity': 100,
                'message': f'CRITICAL: {biomarker_type} dangerously high ({value})',
                'recommendation': 'Immediate medical attention required'
            }

        return {'critical': False}

    def layer3_age_adjusted(self, biomarker: Dict, age: int) -> Dict:
        """Layer 3: Age-adjusted reference ranges"""
        # Simplified age adjustment
        biomarker_type = biomarker['type']
        value = biomarker['value']

        # Age-specific adjustments (simplified)
        adjustments = {
            'glucose': {
                'elderly': (70, 140),  # More lenient for 65+
                'adult': (70, 100),
                'child': (70, 100)
            }
        }

        if biomarker_type in adjustments:
            if age >= 65:
                age_group = 'elderly'
            elif age >= 18:
                age_group = 'adult'
            else:
                age_group = 'child'

            min_val, max_val = adjustments[biomarker_type][age_group]

            if value < min_val or value > max_val:
                return {
                    'anomaly': True,
                    'message': f'{biomarker_type} outside age-adjusted range for {age_group}'
                }

        return {'anomaly': False}

    def layer4_medication_context(self, biomarker: Dict, medications: List[str]) -> Dict:
        """Layer 4: Check biomarker in context of current medications"""
        # Example: High glucose despite being on metformin
        biomarker_type = biomarker['type']

        med_contexts = {
            'glucose': ['metformin', 'insulin', 'glipizide'],
            'systolic_bp': ['amlodipine', 'losartan', 'atenolol'],
            'diastolic_bp': ['amlodipine', 'losartan', 'atenolol'],
            'cholesterol': ['atorvastatin', 'simvastatin']
        }

        if biomarker_type in med_contexts:
            # Extract medication names from prescription dictionaries
            med_names = []
            for med in medications:
                if isinstance(med, dict):
                    med_names.append(med.get('medication', '').lower())
                else:
                    med_names.append(str(med).lower())

            relevant_meds = [m for m in med_names if any(drug in m for drug in med_contexts[biomarker_type])]

            if relevant_meds and biomarker.get('value', 0) > self.biomarker_ranges.get(biomarker_type, {}).get('normal', {}).get('max', float('inf')):
                return {
                    'anomaly': True,
                    'message': f'{biomarker_type} elevated despite medication',
                    'medications': relevant_meds,
                    'recommendation': 'Consider medication adjustment or compliance check'
                }

        return {'anomaly': False}

    def layer5_comorbidity_check(self, biomarkers: List[Dict], diseases: List[str]) -> List[Dict]:
        """Layer 5: Check for patterns related to comorbidities"""
        anomalies = []

        # Extract disease names
        disease_names = []
        for disease in diseases:
            if isinstance(disease, dict):
                disease_names.append(disease.get('text', '').lower())
            else:
                disease_names.append(str(disease).lower())

        # Diabetes + High BP pattern
        has_diabetes = any('diabetes' in d for d in disease_names)
        glucose_values = [b['value'] for b in biomarkers if b['type'] == 'glucose']
        systolic_bp_values = [b['value'] for b in biomarkers if b['type'] == 'systolic_bp']

        if has_diabetes and glucose_values and systolic_bp_values:
            if glucose_values[0] > 180 and systolic_bp_values[0] > 140:
                anomalies.append({
                    'pattern': 'diabetes_hypertension',
                    'severity': 80,
                    'message': 'Poorly controlled diabetes with hypertension',
                    'recommendation': 'Comprehensive cardiovascular risk assessment needed'
                })

        return anomalies

    def layer6_trend_analysis(self, current_biomarkers: List[Dict], historical_biomarkers: List[Dict]) -> List[Dict]:
        """Layer 6: Analyze trends over time"""
        anomalies = []

        # Compare current vs last reading
        for current in current_biomarkers:
            biomarker_type = current['type']
            historical = [h for h in historical_biomarkers if h['type'] == biomarker_type]

            if historical:
                last_value = historical[-1]['value']
                current_value = current['value']
                change_percent = ((current_value - last_value) / last_value) * 100

                # Flag rapid changes (>20%)
                if abs(change_percent) > 20:
                    anomalies.append({
                        'type': 'rapid_change',
                        'biomarker': biomarker_type,
                        'change': f'{change_percent:.1f}%',
                        'severity': min(abs(change_percent), 100),
                        'message': f'Rapid change in {biomarker_type}'
                    })

        return anomalies

    def layer7_drug_interactions(self, medications: List[str]) -> List[Dict]:
        """Layer 7: Check for drug-drug interactions"""
        interactions = []

        # Extract medication names
        med_names = []
        for med in medications:
            if isinstance(med, dict):
                med_names.append(med.get('medication', '').lower())
            else:
                med_names.append(str(med).lower())

        for i, med1 in enumerate(med_names):
            for med2 in med_names[i+1:]:
                # Check interaction database
                for interaction in self.drug_interactions:
                    drug1_lower = interaction['drug1'].lower()
                    drug2_lower = interaction['drug2'].lower()

                    if (drug1_lower in med1 and drug2_lower in med2) or \
                       (drug2_lower in med1 and drug1_lower in med2):
                        interactions.append({
                            'drugs': [med1, med2],
                            'severity': interaction['severity'],
                            'description': interaction['description'],
                            'recommendation': interaction.get('recommendation', 'Consult physician')
                        })

        return interactions

    def detect_anomalies(self, record: Dict) -> Dict:
        """Run all 7 layers of anomaly detection"""
        results = {
            'overall_severity': 0,
            'anomalies': [],
            'critical_alerts': [],
            'recommendations': []
        }

        biomarkers = record.get('biomarkers', [])
        medications = record.get('medications', [])
        diseases = record.get('diseases', [])
        age = record.get('patient_age', 50)
        historical = record.get('historical_biomarkers', [])

        # Layer 1-3: Per biomarker checks
        for biomarker in biomarkers:
            l1 = self.layer1_range_check(biomarker)
            if l1.get('anomaly'):
                results['anomalies'].append(l1)
                results['overall_severity'] = max(results['overall_severity'], l1.get('severity', 0))

            l2 = self.layer2_critical_check(biomarker)
            if l2.get('critical'):
                results['critical_alerts'].append(l2)
                results['overall_severity'] = 100
                results['recommendations'].append(l2.get('recommendation'))

            l3 = self.layer3_age_adjusted(biomarker, age)
            if l3.get('anomaly'):
                results['anomalies'].append(l3)

            l4 = self.layer4_medication_context(biomarker, medications)
            if l4.get('anomaly'):
                results['anomalies'].append(l4)
                if l4.get('recommendation'):
                    results['recommendations'].append(l4.get('recommendation'))

        # Layer 5: Comorbidity patterns
        l5_anomalies = self.layer5_comorbidity_check(biomarkers, diseases)
        results['anomalies'].extend(l5_anomalies)
        for anomaly in l5_anomalies:
            results['overall_severity'] = max(results['overall_severity'], anomaly.get('severity', 0))
            if anomaly.get('recommendation'):
                results['recommendations'].append(anomaly['recommendation'])

        # Layer 6: Trend analysis
        if historical:
            l6_anomalies = self.layer6_trend_analysis(biomarkers, historical)
            results['anomalies'].extend(l6_anomalies)

        # Layer 7: Drug interactions
        l7_interactions = self.layer7_drug_interactions(medications)
        if l7_interactions:
            results['drug_interactions'] = l7_interactions
            for interaction in l7_interactions:
                if interaction['severity'] == 'high':
                    results['overall_severity'] = max(results['overall_severity'], 80)

        return results

    def _calculate_severity(self, value: float, threshold: float, critical: float) -> int:
        """Calculate severity score (0-100)"""
        distance_from_normal = abs(value - threshold)
        distance_to_critical = abs(critical - threshold)

        if distance_to_critical == 0:
            return 50

        severity = min(100, (distance_from_normal / distance_to_critical) * 100)
        return int(severity)
