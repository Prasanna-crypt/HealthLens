def check_report_quality(classified_results):
    issues = []
    
    if not classified_results:
        issues.append({"type": "empty_report", "message": "No tests could be extracted from the document."})
        return issues
        
    test_names = set()
    
    for idx, res in enumerate(classified_results):
        name = res.get('test_name', '')
        val = res.get('value')
        unit = res.get('unit', '')
        conf = res.get('confidence', 1.0)
        
        if not name:
            issues.append({"type": "missing_name", "index": idx, "message": f"Test name missing at position {idx+1}"})
        else:
            if name in test_names:
                issues.append({"type": "duplicate_test", "test_name": name, "message": f"Duplicate test found: {name}"})
            test_names.add(name)
            
        if val is None:
            issues.append({"type": "missing_value", "test_name": name, "message": f"Value missing for {name}"})
            
        if not unit:
            issues.append({"type": "missing_unit", "test_name": name, "message": f"Unit missing for {name}"})
            
        if conf < 0.8:
            issues.append({"type": "low_confidence", "test_name": name, "message": f"Low OCR confidence for {name}"})
            
        if res.get('reference_low') is None or res.get('reference_high') is None:
            issues.append({"type": "missing_range", "test_name": name, "message": f"Reference range missing for {name}"})
            
    return issues
