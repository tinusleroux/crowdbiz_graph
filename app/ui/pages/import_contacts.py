"""
Import Contacts Page
CSV file import with privacy filtering
"""

import streamlit as st
import pandas as pd
import io

from ...services.import_service import get_import_service
from ...core.logger import get_logger

logger = get_logger("import_contacts_page")

def show_import_contacts():
    """Display the import contacts page"""
    
    st.title("📥 Import Professional Contacts")
    
    st.markdown("""
    Import professional contacts from CSV files with **automatic privacy filtering**.
    
    ⚠️ **Privacy Protection**: The system automatically removes personal information like:
    - 🚫 Email addresses, phone numbers, home addresses
    - 🚫 Personal notes, salary information, private data
    - ✅ Only professional information is stored (names, titles, organizations)
    """)
    
    # Get import service
    import_service = get_import_service()
    
    # File upload section
    st.markdown("---")
    st.markdown("### 📁 Upload CSV File")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file containing professional contact information"
    )
    
    if uploaded_file is not None:
        try:
            # Read and validate CSV
            file_content = uploaded_file.getvalue()
            
            with st.spinner("Analyzing CSV structure..."):
                validation_report = import_service.validate_csv_structure(
                    file_content, uploaded_file.name
                )
            
            if validation_report['valid']:
                # Show CSV preview and column mapping
                show_csv_preview_and_mapping(validation_report, file_content, uploaded_file.name)
            else:
                st.error("CSV Validation Failed")
                st.error(validation_report.get('error', 'Unknown error'))
                
        except Exception as e:
            logger.error(f"Error processing uploaded file: {e}")
            st.error("Error reading CSV file. Please check the file format and try again.")
            st.error(str(e))
    
    # Import instructions
    show_import_instructions()

def show_csv_preview_and_mapping(validation_report, file_content, filename):
    """Show CSV preview and handle column mapping"""
    
    st.success("✅ CSV file is valid and ready for import")
    
    # Show validation summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", validation_report['total_rows'])
    
    with col2:
        st.metric("Total Columns", validation_report['total_columns'])
    
    with col3:
        st.metric("Allowed Columns", len(validation_report['allowed_columns']))
    
    with col4:
        st.metric("Filtered Columns", len(validation_report['filtered_columns']))
    
    # Show filtered columns warning
    if validation_report['filtered_columns']:
        st.warning("🔒 **Privacy Protection Active**")
        st.write("The following columns were filtered out for privacy:")
        filtered_cols_text = ", ".join(validation_report['filtered_columns'])
        st.code(filtered_cols_text)
    
    # Column mapping section
    st.markdown("---")
    st.markdown("### 🔗 Column Mapping")
    st.write("Map your CSV columns to database fields:")
    
    # Create column mapping interface
    mapping = {}
    suggested_mapping = validation_report.get('column_suggestions', {})
    
    # Available database fields
    db_fields = [
        'full_name', 'first_name', 'last_name', 'job_title', 
        'organization', 'department', 'linkedin_url', '-- Skip Column --'
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Your CSV Columns:**")
        for csv_column in validation_report['allowed_columns']:
            st.write(f"• {csv_column}")
    
    with col2:
        st.write("**Map to Database Fields:**")
        for csv_column in validation_report['allowed_columns']:
            # Use suggested mapping as default
            suggested_field = suggested_mapping.get(csv_column, '-- Skip Column --')
            if suggested_field not in db_fields:
                suggested_field = '-- Skip Column --'
            
            selected_field = st.selectbox(
                f"Map '{csv_column}' to:",
                db_fields,
                index=db_fields.index(suggested_field),
                key=f"mapping_{csv_column}"
            )
            
            if selected_field != '-- Skip Column --':
                mapping[csv_column] = selected_field
    
    # Data preview
    if validation_report.get('sample_data'):
        st.markdown("---")
        st.markdown("### 👀 Data Preview")
        st.write("First 5 rows of your data:")
        
        preview_df = pd.DataFrame(validation_report['sample_data'])
        st.dataframe(preview_df, use_container_width=True)
    
    # Import button
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Import Data", type="primary", use_container_width=True):
            if mapping:
                perform_import(file_content, filename, mapping)
            else:
                st.error("Please map at least one column before importing")
    
    with col2:
        if st.button("🔄 Reset Upload", use_container_width=True):
            st.rerun()

def perform_import(file_content, filename, column_mapping):
    """Perform the actual import operation"""
    
    import_service = get_import_service()
    
    with st.spinner("Importing contacts with privacy filtering..."):
        try:
            # Perform import
            import_result = import_service.import_csv_file(
                file_content, filename, column_mapping
            )
            
            # Display results
            st.markdown("---")
            st.markdown("### 📊 Import Results")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("✅ Imported", import_result.imported, 
                         delta=f"+{import_result.imported}")
            
            with col2:
                st.metric("🔄 Updated", import_result.updated,
                         delta=f"+{import_result.updated}")
            
            with col3:
                st.metric("⏭️ Skipped", import_result.skipped)
            
            with col4:
                st.metric("📊 Total Processed", import_result.total)
            
            # Success message
            if import_result.imported > 0 or import_result.updated > 0:
                st.success(f"✅ Import completed successfully! "
                          f"{import_result.imported} new contacts created, "
                          f"{import_result.updated} contacts updated.")
            
            # Privacy filtering report
            if import_result.privacy_filtered_fields:
                st.info("🔒 **Privacy Protection Applied**")
                st.write("The following fields were filtered for privacy compliance:")
                filtered_text = ", ".join(import_result.privacy_filtered_fields)
                st.code(filtered_text)
            
            # Show errors if any
            if import_result.errors:
                st.warning(f"⚠️ {len(import_result.errors)} errors occurred:")
                for error in import_result.errors[:10]:  # Show first 10 errors
                    st.error(error)
                
                if len(import_result.errors) > 10:
                    st.info(f"... and {len(import_result.errors) - 10} more errors")
            
            # Show warnings if any
            if import_result.warnings:
                for warning in import_result.warnings[:5]:
                    st.warning(warning)
        
        except Exception as e:
            logger.error(f"Import operation failed: {e}")
            st.error("Import failed. Please check your data and try again.")
            st.error(str(e))

def show_import_instructions():
    """Show CSV import instructions and requirements"""
    
    st.markdown("---")
    st.markdown("### 📋 Import Instructions")
    
    with st.expander("📖 CSV Format Requirements"):
        st.markdown("""
        **Required CSV Format:**
        
        - 📄 **File Type**: CSV (Comma Separated Values)
        - 📊 **Headers**: First row should contain column headers
        - 💾 **Encoding**: UTF-8 recommended
        - 🔤 **Name Field**: At least one name field is required (full_name, first_name + last_name)
        
        **Recommended Columns:**
        - `full_name` or `first_name` + `last_name` (required)
        - `job_title` - Professional title or role
        - `organization` - Company or team name  
        - `department` - Department or division
        - `linkedin_url` - LinkedIn profile URL
        
        **Privacy Note:** 
        Columns containing personal information (email, phone, address) will be automatically filtered out.
        """)
    
    with st.expander("💡 Import Tips"):
        st.markdown("""
        **Best Practices:**
        
        1. **Clean Your Data**: Remove or fix any obvious errors before importing
        2. **Name Formats**: Use consistent name formatting (e.g., "John Smith")
        3. **Organization Names**: Use full, official organization names
        4. **LinkedIn URLs**: Include full URLs (https://linkedin.com/in/...)
        5. **Test with Small Files**: Try importing a small sample first
        
        **Common Issues:**
        - Empty name fields will cause records to be skipped
        - Duplicate names may result in updates rather than new records
        - Invalid LinkedIn URLs will be skipped
        """)
    
    with st.expander("🔒 Privacy Protection Details"):
        st.markdown("""
        **Automatically Filtered Fields:**
        
        The system protects privacy by automatically removing:
        
        - 📧 **Email addresses** (any field containing 'email', 'mail', '@')
        - 📱 **Phone numbers** (any field containing 'phone', 'mobile', 'cell')
        - 🏠 **Addresses** (any field containing 'address', 'street', 'zip')
        - 💰 **Financial information** (salary, compensation, pay)
        - 📝 **Personal notes** (any private or confidential fields)
        - 🎂 **Personal details** (birthday, age, personal information)
        
        **What We Keep:**
        - ✅ Professional names and titles
        - ✅ Organization and department information
        - ✅ Public professional profiles (LinkedIn)
        - ✅ Professional skills and experience
        """)
