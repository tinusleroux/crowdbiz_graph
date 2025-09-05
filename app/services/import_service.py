"""
CSV Import Service
Handles CSV data import with privacy filtering and validation
"""

import pandas as pd
import io
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import uuid

from ..core.privacy import (
    filter_csv_columns, 
    sanitize_dataset_for_storage, 
    validate_privacy_compliance,
    PrivacyFilter
)
from ..core.database import get_database_manager, insert_data
from ..core.logger import get_logger
from ..core.models import ImportResult, validate_import_data

logger = get_logger("import_service")

class ImportService:
    """Service for handling CSV data imports"""
    
    def __init__(self):
        self.privacy_filter = PrivacyFilter()
        self.db_manager = get_database_manager()
    
    def import_csv_file(self, file_content: bytes, filename: str, 
                       column_mapping: Dict[str, str] = None) -> ImportResult:
        """
        Import CSV file with privacy filtering and validation
        
        Args:
            file_content: Raw CSV file bytes
            filename: Name of the uploaded file
            column_mapping: Mapping of CSV columns to database fields
        
        Returns:
            ImportResult with details of the import operation
        """
        logger.info(f"Starting CSV import: {filename}")
        
        try:
            # Read CSV data
            df = pd.read_csv(io.BytesIO(file_content))
            logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Filter sensitive columns
            allowed_columns, filtered_columns = filter_csv_columns(df.columns.tolist())
            
            if not allowed_columns:
                return ImportResult(
                    source=filename,
                    errors=["No valid columns found after privacy filtering"],
                    privacy_filtered_fields=filtered_columns
                )
            
            # Keep only allowed columns
            df_filtered = df[allowed_columns]
            
            # Convert to list of dictionaries
            records = df_filtered.to_dict('records')
            
            # Apply privacy filtering to data
            sanitized_records, privacy_report = sanitize_dataset_for_storage(records)
            
            # Validate import data structure
            valid_contacts, validation_errors = validate_import_data(sanitized_records)
            
            # Apply column mapping if provided
            if column_mapping:
                valid_contacts = self._apply_column_mapping(valid_contacts, column_mapping)
            
            # Import valid contacts
            import_results = self._import_contacts_to_database(valid_contacts, filename)
            
            # Create comprehensive result
            result = ImportResult(
                source=filename,
                imported=import_results['imported'],
                updated=import_results['updated'],
                skipped=len(records) - len(valid_contacts),
                total=len(records),
                errors=validation_errors + import_results['errors'],
                warnings=import_results['warnings'],
                privacy_filtered_fields=filtered_columns + privacy_report.get('sensitive_fields_removed', [])
            )
            
            logger.info(f"Import completed: {result.imported} imported, {result.updated} updated, "
                       f"{result.skipped} skipped, {len(result.errors)} errors")
            
            return result
            
        except Exception as e:
            logger.error(f"CSV import failed: {e}")
            return ImportResult(
                source=filename,
                errors=[f"Import failed: {str(e)}"],
                total=0
            )
    
    def _apply_column_mapping(self, records: List[Dict], mapping: Dict[str, str]) -> List[Dict]:
        """Apply column mapping to transform field names"""
        mapped_records = []
        
        for record in records:
            mapped_record = {}
            
            for csv_col, db_field in mapping.items():
                if csv_col in record:
                    mapped_record[db_field] = record[csv_col]
            
            # Keep unmapped fields as they are
            for key, value in record.items():
                if key not in mapping:
                    mapped_record[key] = value
            
            mapped_records.append(mapped_record)
        
        return mapped_records
    
    def _import_contacts_to_database(self, contacts: List[Dict], source: str) -> Dict[str, Any]:
        """Import contacts to the database"""
        results = {
            'imported': 0,
            'updated': 0,
            'errors': [],
            'warnings': []
        }
        
        if not self.db_manager.is_connected():
            results['errors'].append("Database connection not available")
            return results
        
        for i, contact in enumerate(contacts):
            try:
                # Add metadata
                contact_data = contact.copy()
                contact_data['id'] = str(uuid.uuid4())
                contact_data['created_at'] = datetime.now()
                contact_data['updated_at'] = datetime.now()
                contact_data['source'] = source
                
                # Check if contact already exists (by name)
                existing = self._find_existing_contact(contact_data['full_name'])
                
                if existing:
                    # Update existing contact
                    updated_data = self._merge_contact_data(existing, contact_data)
                    if self._update_contact(existing['id'], updated_data):
                        results['updated'] += 1
                        logger.debug(f"Updated contact: {contact_data['full_name']}")
                    else:
                        results['errors'].append(f"Failed to update contact: {contact_data['full_name']}")
                else:
                    # Insert new contact
                    if insert_data('person', contact_data):
                        results['imported'] += 1
                        logger.debug(f"Imported contact: {contact_data['full_name']}")
                    else:
                        results['errors'].append(f"Failed to import contact: {contact_data['full_name']}")
                
            except Exception as e:
                results['errors'].append(f"Contact {i+1} ({contact.get('full_name', 'Unknown')}): {str(e)}")
                logger.error(f"Error importing contact {i+1}: {e}")
        
        return results
    
    def _find_existing_contact(self, full_name: str) -> Optional[Dict]:
        """Find existing contact by name"""
        try:
            results = self.db_manager.safe_query(
                'person',
                'select',
                filters={'full_name': full_name},
                limit=1
            )
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error finding existing contact: {e}")
            return None
    
    def _merge_contact_data(self, existing: Dict, new_data: Dict) -> Dict:
        """Merge new contact data with existing data"""
        merged = existing.copy()
        
        # Update with non-empty new values
        for key, value in new_data.items():
            if value and (key not in merged or not merged[key]):
                merged[key] = value
        
        # Always update timestamp and source
        merged['updated_at'] = datetime.now()
        merged['source'] = new_data.get('source', merged.get('source', 'Unknown'))
        
        return merged
    
    def _update_contact(self, contact_id: str, data: Dict) -> bool:
        """Update existing contact in database"""
        try:
            result = self.db_manager.safe_query(
                'person',
                'update',
                data=data,
                filters={'id': contact_id}
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error updating contact {contact_id}: {e}")
            return False
    
    def get_import_column_suggestions(self, csv_columns: List[str]) -> Dict[str, str]:
        """
        Suggest column mappings for CSV import
        Returns mapping of CSV columns to database fields
        """
        suggestions = {}
        
        # Common column mappings
        column_patterns = {
            'full_name': ['name', 'full_name', 'fullname', 'contact_name', 'person_name'],
            'first_name': ['first_name', 'firstname', 'first', 'fname'],
            'last_name': ['last_name', 'lastname', 'last', 'lname', 'surname'],
            'job_title': ['title', 'job_title', 'position', 'role', 'job', 'job_position'],
            'organization': ['organization', 'company', 'employer', 'org', 'team'],
            'department': ['department', 'dept', 'division', 'unit'],
            'linkedin_url': ['linkedin', 'linkedin_url', 'linkedin_profile', 'profile_url']
        }
        
        # Match CSV columns to database fields
        for csv_col in csv_columns:
            csv_col_lower = csv_col.lower().strip()
            
            for db_field, patterns in column_patterns.items():
                if csv_col_lower in patterns or any(pattern in csv_col_lower for pattern in patterns):
                    suggestions[csv_col] = db_field
                    break
        
        return suggestions
    
    def validate_csv_structure(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Validate CSV structure and provide import preview
        Returns validation report with recommendations
        """
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            
            # Filter columns for privacy
            allowed_columns, filtered_columns = filter_csv_columns(df.columns.tolist())
            
            # Get column mapping suggestions
            column_suggestions = self.get_import_column_suggestions(allowed_columns)
            
            # Sample data preview (first 5 rows)
            sample_data = df[allowed_columns].head(5).to_dict('records') if allowed_columns else []
            
            return {
                'valid': len(allowed_columns) > 0,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'allowed_columns': allowed_columns,
                'filtered_columns': filtered_columns,
                'column_suggestions': column_suggestions,
                'sample_data': sample_data,
                'recommended_mapping': column_suggestions,
                'warnings': [
                    f"Filtered {len(filtered_columns)} sensitive columns"
                ] if filtered_columns else []
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'total_rows': 0,
                'total_columns': 0,
                'allowed_columns': [],
                'filtered_columns': [],
                'sample_data': []
            }

# Global import service instance
_import_service: Optional[ImportService] = None

def get_import_service() -> ImportService:
    """Get or create the global import service instance"""
    global _import_service
    if _import_service is None:
        _import_service = ImportService()
    return _import_service
