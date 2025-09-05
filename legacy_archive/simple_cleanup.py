#!/usr/bin/env python3
"""
Simple API-based cleanup for corrupted contacts
"""

import json
import subprocess
import sys

def run_curl(endpoint, method="GET", data=None):
    """Run curl command and return JSON response"""
    cmd = ["curl", "-s", "-X", method, f"http://localhost:8000{endpoint}"]
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error running curl: {e}")
        return None

def analyze_records():
    """Analyze current records via API"""
    print("📊 Analyzing current records...")
    
    # Get all people
    people = run_curl("/people?limit=2000")
    if not people:
        print("❌ Failed to fetch people")
        return []
    
    # Check if we got an error response
    if isinstance(people, dict) and 'detail' in people:
        print(f"❌ API Error: {people['detail']}")
        return []
    
    total = len(people)
    by_date = {}
    incomplete = []
    
    for person in people:
        created_date = person.get('created_at', '')[:10]
        if created_date not in by_date:
            by_date[created_date] = 0
        by_date[created_date] += 1
        
        # Check if incomplete (no LinkedIn and no meaningful name)
        if (not person.get('linkedin_url') and 
            (not person.get('full_name') or len(person.get('full_name', '').strip()) < 2)):
            incomplete.append(person)
    
    print(f"Total records: {total}")
    print("\nRecords by date:")
    for date, count in sorted(by_date.items()):
        marker = " ⚠️" if date == "2025-06-10" else ""
        print(f"  {date}: {count} records{marker}")
    
    print(f"\nIncomplete records (no LinkedIn and no meaningful name): {len(incomplete)}")
    
    if incomplete:
        print("\nSample incomplete records:")
        for i, record in enumerate(incomplete[:10]):
            name = record.get('full_name', 'No name')
            created = record.get('created_at', '')[:10]
            print(f"  {i+1}. '{name}' - {created}")
        
        if len(incomplete) > 10:
            print(f"  ... and {len(incomplete) - 10} more")
    
    return incomplete

def delete_record(person_id):
    """Delete a person record via API"""
    result = run_curl(f"/people/{person_id}", method="DELETE")
    return result is not None

def cleanup_june_10_records():
    """Clean up the corrupted June 10 records"""
    print("\n🧹 Cleaning up June 10, 2025 records...")
    
    # Get all people
    people = run_curl("/people?limit=2000")
    if not people:
        print("❌ Failed to fetch people")
        return
    
    # Filter for June 10 records
    june_10_records = [p for p in people if p['created_at'].startswith('2025-06-10')]
    
    if not june_10_records:
        print("✅ No June 10 records found")
        return
    
    print(f"Found {len(june_10_records)} records from June 10, 2025")
    
    # Show sample
    print("\nSample records to be deleted:")
    for i, record in enumerate(june_10_records[:5]):
        name = record.get('full_name', 'No name')
        linkedin = record.get('linkedin_url', 'No LinkedIn')
        print(f"  {i+1}. '{name}' | LinkedIn: {linkedin}")
    
    if len(june_10_records) > 5:
        print(f"  ... and {len(june_10_records) - 5} more")
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: This will delete {len(june_10_records)} records!")
    confirm = input("Type 'DELETE' to confirm: ").strip()
    
    if confirm != 'DELETE':
        print("❌ Cleanup cancelled")
        return
    
    print("\n🗑️  Deleting records...")
    deleted_count = 0
    failed_count = 0
    
    for i, record in enumerate(june_10_records):
        person_id = record['id']
        name = record.get('full_name', 'No name')
        
        # Actually delete the record using the API
        if delete_record(person_id):
            print(f"Record {i+1}/{len(june_10_records)}: ✅ Deleted '{name}'")
            deleted_count += 1
        else:
            print(f"Record {i+1}/{len(june_10_records)}: ❌ Failed to delete '{name}'")
            failed_count += 1
        
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{len(june_10_records)} records processed...")
    
    print(f"\n✅ Successfully deleted {deleted_count} records")
    if failed_count > 0:
        print(f"❌ Failed to delete {failed_count} records")

def cleanup_incomplete_records():
    """Clean up incomplete records (no LinkedIn and no meaningful name)"""
    print("\n🧹 Cleaning up incomplete records...")
    
    incomplete = analyze_records()
    
    if not incomplete:
        print("✅ No incomplete records found!")
        return
    
    print(f"\n⚠️  WARNING: This will delete {len(incomplete)} incomplete records!")
    confirm = input("Type 'DELETE' to confirm: ").strip()
    
    if confirm != 'DELETE':
        print("❌ Cleanup cancelled")
        return
    
    print(f"\n🗑️  Deleting records...")
    deleted_count = 0
    failed_count = 0
    
    for i, record in enumerate(incomplete):
        person_id = record['id']
        name = record.get('full_name', 'No name')
        
        # Actually delete the record using the API
        if delete_record(person_id):
            print(f"Record {i+1}/{len(incomplete)}: ✅ Deleted '{name}'")
            deleted_count += 1
        else:
            print(f"Record {i+1}/{len(incomplete)}: ❌ Failed to delete '{name}'")
            failed_count += 1
        
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{len(incomplete)} records processed...")
    
    print(f"\n✅ Successfully deleted {deleted_count} records")
    if failed_count > 0:
        print(f"❌ Failed to delete {failed_count} records")

def main():
    """Main cleanup function"""
    print("🧹 Contact Import Cleanup Tool")
    print("=" * 40)
    
    # Analyze current state
    analyze_records()
    
    print("\nCleanup Options:")
    print("1. Clean up all records from June 10, 2025 (corrupted batch)")
    print("2. Clean up incomplete records (no LinkedIn and no meaningful name)")  
    print("3. Just analyze (no cleanup)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        cleanup_june_10_records()
    elif choice == "2":
        cleanup_incomplete_records()
    elif choice == "3":
        print("\n📊 Analysis complete - no cleanup performed")
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main()
