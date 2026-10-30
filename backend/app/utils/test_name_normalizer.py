# TODO: Might need a cleanup later.

import re

# Dictionary to map different variations to a single standard name
TEST_ALIASES = {
    'Hb': 'Hemoglobin', 'HGB': 'Hemoglobin', 'Hgb': 'Hemoglobin', 'Haemoglobin': 'Hemoglobin',
    'WBC': 'WBC', 'White Blood Cell Count': 'WBC', 'White Blood Cells': 'WBC', 'Leukocytes': 'WBC',
    'RBC': 'RBC', 'Red Blood Cell Count': 'RBC', 'Red Blood Cells': 'RBC', 'Erythrocytes': 'RBC', 'Erythrocyte Count': 'RBC',
    'PLT': 'Platelets', 'Platelet Count': 'Platelets', 'Thrombocytes': 'Platelets',
    'HCT': 'Hematocrit', 'Hct': 'Hematocrit', 'PCV': 'Hematocrit', 'P.C.V.': 'Hematocrit',
    'MCV': 'MCV', 'M.C.V.': 'MCV', 'Mean Corpuscular Volume': 'MCV',
    'MCH': 'MCH', 'M.C.H.': 'MCH', 'Mean Corpuscular Hemoglobin': 'MCH',
    'MCHC': 'MCHC', 'M.C.H.C.': 'MCHC', 'Mean Corpuscular Hemoglobin Concentration': 'MCHC',
    'RDW': 'RDW', 'Rdw-CV': 'RDW', 'RDW-CV': 'RDW', 'Red Cell Distribution Width': 'RDW',
    'FBG': 'Fasting Blood Glucose', 'Fasting Glucose': 'Fasting Blood Glucose', 'Blood Sugar': 'Fasting Blood Glucose', 'Glucose': 'Fasting Blood Glucose',
    'Glycated Hemoglobin': 'HbA1c', 'A1C': 'HbA1c', 'Hemoglobin A1c': 'HbA1c',
    'SGPT': 'ALT', 'Alanine Aminotransferase': 'ALT',
    'SGOT': 'AST', 'Aspartate Aminotransferase': 'AST',
    'T.Bil': 'Total Bilirubin', 'Bilirubin Total': 'Total Bilirubin', 'Bilirubin': 'Total Bilirubin', 'Serum Bilirubin': 'Total Bilirubin', 'Serum Bilirubin (Total)': 'Total Bilirubin',
    'Direct Bilirubin': 'Direct Bilirubin', 'Serum Bilirubin (Direct)': 'Direct Bilirubin',
    'Indirect Bilirubin': 'Indirect Bilirubin', 'Serum Bilirubin (Indirect)': 'Indirect Bilirubin',
    'Serum Protein': 'Total Protein', 'Total Protein': 'Total Protein',
    'Alb': 'Albumin', 'Serum Albumin': 'Albumin',
    'Globulin': 'Globulin', 'Serum Globulin': 'Globulin',
    'A/G Ratio': 'A/G Ratio', 'Albumin/Globulin Ratio': 'A/G Ratio',
    'Alk Phos': 'ALP', 'Alkaline Phosphatase': 'ALP',
    'Creat': 'Creatinine', 'Cr': 'Creatinine', 'Serum Creatinine': 'Creatinine',
    'TC': 'Total Cholesterol', 'T.Chol': 'Total Cholesterol', 'Cholesterol': 'Total Cholesterol',
    'TG': 'Triglycerides', 'Trig': 'Triglycerides',
    'LDL': 'LDL Cholesterol', 'LDL-C': 'LDL Cholesterol',
    'HDL': 'HDL Cholesterol', 'HDL-C': 'HDL Cholesterol',
    'BUN': 'BUN', 'Blood Urea Nitrogen': 'BUN', 'Urea': 'BUN', 'Urea Nitrogen': 'BUN',
    'UA': 'Uric Acid', 'Serum Uric Acid': 'Uric Acid',
    'TSH': 'TSH', 'Thyroid Stimulating Hormone': 'TSH',
    'T3': 'T3', 'Triiodothyronine': 'T3', 'Total T3': 'T3',
    'T4': 'T4', 'Thyroxine': 'T4', 'Total T4': 'T4',
    'FT4': 'Free T4', 'Free Thyroxine': 'Free T4',
}

# Standardize units (e.g., making sure uppercase/lowercase matches)
UNIT_NORMALIZATION = {
    'g/dl': 'g/dL', 'mg/dl': 'mg/dL', 'u/l': 'U/L', 'ul': 'µL',
    '10^3/ul': '/µL', '10^6/ul': 'million/µL',
    'gms/dl': 'g/dL', 'gm/dl': 'g/dL', 'gms/dL': 'g/dL', 'gm/dL': 'g/dL',
    'cumm': '/µL', '/cumm': '/µL', 'cu.mm': '/µL', '/cu.mm': '/µL',
    'lakhs/cumm': 'lakhs/cumm', 'lacs/cumm': 'lakhs/cumm'
}

def normalize_test_name(raw_name: str) -> str:
    # Remove extra parenthetical text like "(Impedence)" or "(Colorimetric)" or "(Calculated)" if matching
    clean_name = raw_name.strip()
    base_name = re.sub(r'\s*\([^)]*\)', '', clean_name).strip()
    
    if clean_name in TEST_ALIASES:
        return TEST_ALIASES[clean_name]
    if base_name in TEST_ALIASES:
        return TEST_ALIASES[base_name]

    # Case-insensitive lookup
    clean_lower = clean_name.lower()
    base_lower = base_name.lower()
    for alias, standard in TEST_ALIASES.items():
        al = alias.lower()
        if al == clean_lower or al == base_lower:
            return standard
        
    return clean_name

def normalize_unit(raw_unit: str) -> str:
    if not raw_unit:
        return ""
    clean = raw_unit.strip().lower()
    return UNIT_NORMALIZATION.get(clean, raw_unit.strip())
