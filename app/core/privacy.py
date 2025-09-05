"""
Privacy filtering and data sanitization
Ensures all data complies with privacy-first principles
"""

import re
from typing import Dict, List, Any, Optional
from .logger import get_logger

logger = get_logger("privacy")

# Privacy-sensitive field patterns
SENSITIVE_FIELDS = {
    'email', 'email_address', 'e_mail', 'contact_email', 'personal_email', 
    'work_email', 'business_email', 'mail', 'gmail', 'outlook',
    'phone', 'phone_number', 'mobile', 'cell', 'telephone', 'contact_phone',
    'personal_phone', 'work_phone', 'business_phone', 'tel', 'cell_phone',
    'address', 'street_address', 'home_address', 'mailing_address', 
    'street', 'address_line_1', 'address_line_2', 'street_1', 'street_2',
    'personal_address', 'residence', 'home', 'zip', 'zipcode', 'postal_code',
    'salary', 'compensation', 'wage', 'income', 'pay', 'earnings',
    'ssn', 'social_security', 'tax_id', 'employee_id_private',
    'personal_notes', 'private_notes', 'confidential', 'internal_notes',
    'birthday', 'birth_date', 'date_of_birth', 'dob', 'age'
}

# Email patterns to detect in text
EMAIL_PATTERNS = [
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    r'\b\w+@\w+\.\w+\b'
]

# Phone patterns to detect in text  
PHONE_PATTERNS = [
    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # XXX-XXX-XXXX or XXX.XXX.XXXX
    r'\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (XXX) XXX-XXXX
    r'\b\d{10}\b'  # XXXXXXXXXX
]

def is_sensitive_field(field_name: str) -> bool:
    """Check if a field name indicates sensitive/private data"""
    field_name_lower = field_name.lower().strip()
    
    # Direct match
    if field_name_lower in SENSITIVE_FIELDS:
        return True
    
    # Check for partial matches
    for sensitive_field in SENSITIVE_FIELDS:
        if sensitive_field in field_name_lower or field_name_lower in sensitive_field:
            return True
    
    return False

def contains_email(text: str) -> bool:
    """Check if text contains email addresses"""
    if not text or not isinstance(text, str):
        return False
    
    for pattern in EMAIL_PATTERNS:
        if re.search(pattern, text):
            return True
    
    return False

def contains_phone(text: str) -> bool:
    """Check if text contains phone numbers"""
    if not text or not isinstance(text, str):
        return False
    
    for pattern in PHONE_PATTERNS:
        if re.search(pattern, text):
            return True
    
    return False

def sanitize_text(text: str) -> str:
    """Remove email addresses and phone numbers from text"""
    if not text or not isinstance(text, str):
        return text
    
    sanitized = text
    
    # Remove emails
    for pattern in EMAIL_PATTERNS:
        sanitized = re.sub(pattern, '[EMAIL_REMOVED]', sanitized)
    
    # Remove phone numbers
    for pattern in PHONE_PATTERNS:
        sanitized = re.sub(pattern, '[PHONE_REMOVED]', sanitized)
    
    return sanitized

def filter_csv_columns(columns: List[str]) -> tuple[List[str], List[str]]:
    """
    Filter CSV columns to remove sensitive data fields
    Returns: (allowed_columns, filtered_columns)
    """
    allowed_columns = []
    filtered_columns = []
    
    for column in columns:
        if is_sensitive_field(column):
            filtered_columns.append(column)
            logger.warning(f"Filtered sensitive column: {column}")
        else:
            allowed_columns.append(column)
    
    logger.info(f"CSV column filtering: {len(allowed_columns)} allowed, {len(filtered_columns)} filtered")
    return allowed_columns, filtered_columns

def sanitize_data_for_storage(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize data before storing in database
    Removes sensitive fields and sanitizes text content
    """
    sanitized_data = {}
    removed_fields = []
    
    for key, value in data.items():
        if is_sensitive_field(key):
            removed_fields.append(key)
            continue
        
        # Sanitize text values
        if isinstance(value, str):
            original_value = value
            sanitized_value = sanitize_text(value)
            
            if original_value != sanitized_value:
                logger.warning(f"Sanitized text in field '{key}': found private data")
            
            sanitized_data[key] = sanitized_value
        else:
            sanitized_data[key] = value
    
    if removed_fields:
        logger.info(f"Removed sensitive fields from data: {', '.join(removed_fields)}")
    
    return sanitized_data

def sanitize_data_for_display(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize data before displaying to user
    Additional layer of protection for display
    """
    # For display, we apply the same rules as storage
    return sanitize_data_for_storage(data)

def sanitize_dataset_for_storage(dataset: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Sanitize an entire dataset for storage
    Returns: (sanitized_dataset, privacy_report)
    """
    sanitized_dataset = []
    privacy_report = {
        'total_records': len(dataset),
        'sensitive_fields_removed': set(),
        'records_with_private_data': 0,
        'total_private_data_instances': 0
    }
    
    for record in dataset:
        original_field_count = len(record)
        sanitized_record = sanitize_data_for_storage(record)
        
        # Track removed fields
        removed_fields = set(record.keys()) - set(sanitized_record.keys())
        privacy_report['sensitive_fields_removed'].update(removed_fields)
        
        # Check if record had private data
        if len(sanitized_record) < original_field_count:
            privacy_report['records_with_private_data'] += 1
            privacy_report['total_private_data_instances'] += (original_field_count - len(sanitized_record))
        
        sanitized_dataset.append(sanitized_record)
    
    # Convert set to list for JSON serialization
    privacy_report['sensitive_fields_removed'] = list(privacy_report['sensitive_fields_removed'])
    
    logger.info(f"Dataset sanitization complete: {privacy_report['total_records']} records processed, "
                f"{privacy_report['records_with_private_data']} contained private data")
    
    return sanitized_dataset, privacy_report

def validate_privacy_compliance(data: Any) -> tuple[bool, List[str]]:
    """
    Validate that data complies with privacy rules
    Returns: (is_compliant, list_of_violations)
    """
    violations = []
    
    if isinstance(data, dict):
        # Check single record
        for key, value in data.items():
            if is_sensitive_field(key):
                violations.append(f"Sensitive field '{key}' found in data")
            
            if isinstance(value, str):
                if contains_email(value):
                    violations.append(f"Email address found in field '{key}'")
                if contains_phone(value):
                    violations.append(f"Phone number found in field '{key}'")
    
    elif isinstance(data, list):
        # Check dataset
        for i, record in enumerate(data):
            if isinstance(record, dict):
                record_violations = validate_privacy_compliance(record)[1]
                for violation in record_violations:
                    violations.append(f"Record {i}: {violation}")
    
    is_compliant = len(violations) == 0
    
    if not is_compliant:
        logger.warning(f"Privacy compliance check failed: {len(violations)} violations found")
        for violation in violations[:10]:  # Log first 10 violations
            logger.warning(f"  - {violation}")
    
    return is_compliant, violations

def get_privacy_safe_fields() -> List[str]:
    """Get list of fields that are safe for professional networking"""
    return [
        'full_name', 'first_name', 'last_name', 'name',
        'title', 'job_title', 'position', 'role',
        'organization', 'company', 'employer', 'team',
        'department', 'division', 'unit',
        'industry', 'sector', 'field',
        'linkedin_url', 'linkedin_profile', 'linkedin',
        'twitter_url', 'twitter_handle', 'twitter',
        'professional_website', 'website', 'portfolio_url',
        'bio', 'biography', 'description', 'about',
        'skills', 'expertise', 'specialization',
        'education', 'university', 'college', 'degree',
        'experience_years', 'years_experience', 'seniority',
        'location_city', 'city', 'metro_area',
        'location_state', 'state', 'region',
        'location_country', 'country',
        'public_achievements', 'awards', 'recognition',
        'certifications', 'licenses', 'credentials'
    ]

class PrivacyFilter:
    """Privacy filter for processing data streams"""
    
    def __init__(self):
        self.violations_count = 0
        self.filtered_fields_count = 0
        self.processed_records_count = 0
    
    def process_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single record through privacy filter"""
        self.processed_records_count += 1
        return sanitize_data_for_storage(record)
    
    def process_dataset(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process entire dataset through privacy filter"""
        return [self.process_record(record) for record in dataset]
    
    def get_statistics(self) -> Dict[str, int]:
        """Get filtering statistics"""
        return {
            'processed_records': self.processed_records_count,
            'violations_found': self.violations_count,
            'fields_filtered': self.filtered_fields_count
        }
