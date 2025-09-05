#!/usr/bin/env python3
"""
Cleanup Script for Corrupted Contact Imports
Removes incomplete contact records from failed import batches
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_API_KEY')
)

def find_incomplete_records():
    """Find records that are incomplete (missing LinkedIn URL - the only public identifier we track)"""
    print("🔍 Finding incomplete records...")
    
    # Get all person records
    result = supabase.table('person').select('*').execute()
    
    incomplete_records = []
    for person in result.data:
        # Check if record is incomplete (no LinkedIn URL and no meaningful name)
        if (not person.get('linkedin_url') and 
            (not person.get('full_name') or len(person.get('full_name', '').strip()) < 2)):
            incomplete_records.append(person)
    
    return incomplete_records

def find_records_by_date(target_date):
    """Find records created on a specific date"""
    print(f"🔍 Finding records created on {target_date}...")
    
    # Get records from specific date
    result = supabase.table('person').select('*').gte('created_at', f'{target_date}T00:00:00').lt('created_at', f'{target_date}T23:59:59').execute()
    
    return result.data

def analyze_records():
    """Analyze the current state of records"""
    print("📊 Analyzing current records...")
    
    # Get all records
    result = supabase.table('person').select('id, full_name, linkedin_url, created_at').execute()
    
    total = len(result.data)
    by_date = {}
    incomplete = []
    
    for person in result.data:
        created_date = person['created_at'][:10]
        if created_date not in by_date:
            by_date[created_date] = 0
        by_date[created_date] += 1
        
        # Check if incomplete
        if (not person.get('linkedin_url') and 
            (not person.get('full_name') or len(person.get('full_name', '').strip()) < 2)):
            incomplete.append(person)
    
    print(f"Total records: {total}")
    print("\nRecords by date:")
    for date, count in sorted(by_date.items()):
        print(f"  {date}: {count} records")
    
    print(f"\nIncomplete records: {len(incomplete)}")
    
    return incomplete

def cleanup_incomplete_records(dry_run=True):
    """Remove incomplete records"""
    incomplete = find_incomplete_records()
    
    if not incomplete:
        print("✅ No incomplete records found!")
        return
    
    print(f"Found {len(incomplete)} incomplete records")
    
    if dry_run:
        print("\n🔍 DRY RUN - No records will be deleted")
        print("Sample incomplete records:")
        for i, record in enumerate(incomplete[:10]):
            print(f"  {i+1}. {record['full_name']} (ID: {record['id'][:8]}...) - {record['created_at'][:10]}")
        
        if len(incomplete) > 10:
            print(f"  ... and {len(incomplete) - 10} more")
        
        return incomplete
    
    print(f"\n⚠️  WARNING: About to delete {len(incomplete)} records!")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != 'DELETE':
        print("❌ Cleanup cancelled")
        return
    
    print("🗑️  Deleting incomplete records...")
    deleted_count = 0
    
    for record in incomplete:
        try:
            # Delete the person record
            supabase.table('person').delete().eq('id', record['id']).execute()
            deleted_count += 1
            
            if deleted_count % 50 == 0:
                print(f"  Deleted {deleted_count}/{len(incomplete)} records...")
                
        except Exception as e:
            print(f"  ❌ Failed to delete {record['full_name']}: {e}")
    
    print(f"✅ Cleanup complete! Deleted {deleted_count} incomplete records")

def cleanup_by_date(target_date, dry_run=True):
    """Remove all records from a specific date"""
    records = find_records_by_date(target_date)
    
    if not records:
        print(f"✅ No records found for {target_date}")
        return
    
    print(f"Found {len(records)} records from {target_date}")
    
    if dry_run:
        print(f"\n🔍 DRY RUN - No records will be deleted")
        print(f"Records from {target_date}:")
        for i, record in enumerate(records[:10]):
            linkedin = record.get('linkedin_url', 'No LinkedIn')
            print(f"  {i+1}. {record['full_name']} | LinkedIn: {linkedin}")
        
        if len(records) > 10:
            print(f"  ... and {len(records) - 10} more")
        
        return records
    
    print(f"\n⚠️  WARNING: About to delete {len(records)} records from {target_date}!")
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != 'DELETE':
        print("❌ Cleanup cancelled")
        return
    
    print(f"🗑️  Deleting records from {target_date}...")
    deleted_count = 0
    
    for record in records:
        try:
            # Delete the person record (roles will be deleted via CASCADE)
            supabase.table('person').delete().eq('id', record['id']).execute()
            deleted_count += 1
            
            if deleted_count % 50 == 0:
                print(f"  Deleted {deleted_count}/{len(records)} records...")
                
        except Exception as e:
            print(f"  ❌ Failed to delete {record['full_name']}: {e}")
    
    print(f"✅ Cleanup complete! Deleted {deleted_count} records from {target_date}")

def main():
    """Main cleanup function"""
    print("🧹 Contact Import Cleanup Tool")
    print("=" * 40)
    
    # First, analyze current state
    analyze_records()
    
    print("\nCleanup Options:")
    print("1. Clean up incomplete records (missing LinkedIn URL and meaningful name)")
    print("2. Clean up all records from June 10, 2025 (corrupted batch)")
    print("3. Just analyze (no cleanup)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        print("\n🧹 Cleaning up incomplete records...")
        
        # First do a dry run
        incomplete = cleanup_incomplete_records(dry_run=True)
        
        if incomplete:
            proceed = input(f"\nProceed with deleting {len(incomplete)} incomplete records? (y/N): ").strip().lower()
            if proceed == 'y':
                cleanup_incomplete_records(dry_run=False)
    
    elif choice == "2":
        print("\n🧹 Cleaning up records from June 10, 2025...")
        
        # First do a dry run
        june_10_records = cleanup_by_date("2025-06-10", dry_run=True)
        
        if june_10_records:
            proceed = input(f"\nProceed with deleting {len(june_10_records)} records from June 10? (y/N): ").strip().lower()
            if proceed == 'y':
                cleanup_by_date("2025-06-10", dry_run=False)
    
    elif choice == "3":
        print("\n📊 Analysis complete - no cleanup performed")
    
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main()
