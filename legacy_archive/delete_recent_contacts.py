#!/usr/bin/env python3
"""
Delete all contacts added in the past 24 hours
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta

def run_curl(endpoint, method="GET", data=None):
    """Run curl command and return JSON response"""
    cmd = ["curl", "-s", "-X", method, f"http://localhost:8000{endpoint}"]
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            response = result.stdout.strip()
            if response:
                return json.loads(response)
            else:
                return {"success": True}
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error running curl: {e}")
        return None

def get_all_people():
    """Get all people from the API"""
    all_people = []
    limit = 1000
    offset = 0
    
    while True:
        people = run_curl(f"/people?limit={limit}&offset={offset}")
        if not people or len(people) == 0:
            break
        
        all_people.extend(people)
        
        if len(people) < limit:
            break
        
        offset += limit
    
    return all_people

def find_recent_contacts(hours=24):
    """Find contacts created in the past N hours"""
    print(f"🔍 Finding contacts created in the past {hours} hours...")
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(hours=hours)
    cutoff_str = cutoff_time.strftime("%Y-%m-%d")
    
    print(f"Cutoff date: {cutoff_str}")
    
    # Get all people
    all_people = get_all_people()
    
    if not all_people:
        print("❌ Failed to fetch people")
        return []
    
    print(f"Total people in database: {len(all_people)}")
    
    # Filter for recent contacts
    recent_contacts = []
    for person in all_people:
        created_at = person.get('created_at', '')
        if created_at >= f"{cutoff_str}T00:00:00":
            recent_contacts.append(person)
    
    return recent_contacts

def delete_contacts(contacts, dry_run=True):
    """Delete the specified contacts"""
    if not contacts:
        print("✅ No contacts to delete")
        return
    
    print(f"\n{'🔍 DRY RUN - ' if dry_run else '🗑️  DELETING '}Found {len(contacts)} recent contacts")
    
    # Show sample
    print("\nRecent contacts to be deleted:")
    for i, contact in enumerate(contacts[:10]):
        name = contact.get('full_name', 'No name')
        linkedin = contact.get('linkedin_url', 'No LinkedIn')
        created = contact.get('created_at', 'Unknown')[:10] if contact.get('created_at') else 'Unknown'
        
        print(f"  {i+1}. '{name}' | LinkedIn: {linkedin} | {created}")
    
    if len(contacts) > 10:
        print(f"  ... and {len(contacts) - 10} more")
    
    if dry_run:
        print(f"\n🔍 DRY RUN COMPLETE - {len(contacts)} contacts would be deleted")
        return contacts
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: This will permanently delete {len(contacts)} contacts!")
    confirm = input("Type 'DELETE' to confirm: ").strip()
    
    if confirm != 'DELETE':
        print("❌ Deletion cancelled")
        return
    
    print(f"\n🗑️  Deleting {len(contacts)} contacts...")
    deleted_count = 0
    failed_count = 0
    
    for i, contact in enumerate(contacts):
        person_id = contact['id']
        name = contact.get('full_name', 'No name')
        
        result = run_curl(f"/people/{person_id}", method="DELETE")
        
        if result is not None:
            deleted_count += 1
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i+1}/{len(contacts)} contacts processed...")
        else:
            failed_count += 1
            print(f"  ❌ Failed to delete: {name}")
    
    print(f"\n✅ Deletion complete!")
    print(f"   Deleted: {deleted_count}")
    print(f"   Failed: {failed_count}")

def main():
    """Main function"""
    print("🗑️  Delete Recent Contacts Tool")
    print("=" * 40)
    
    print("Options:")
    print("1. Delete contacts from past 24 hours (June 12-13, 2025)")
    print("2. Delete contacts from past 48 hours (June 11-13, 2025)")
    print("3. Delete contacts from past 72 hours (June 10-13, 2025)")
    print("4. Custom hours")
    print("5. Just analyze (no deletion)")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    hours = 24
    if choice == "1":
        hours = 24
    elif choice == "2":
        hours = 48
    elif choice == "3":
        hours = 72
    elif choice == "4":
        try:
            hours = int(input("Enter number of hours: ").strip())
        except ValueError:
            print("❌ Invalid number")
            return
    elif choice == "5":
        hours = 24
    else:
        print("❌ Invalid option")
        return
    
    # Find recent contacts
    recent_contacts = find_recent_contacts(hours)
    
    if not recent_contacts:
        print("✅ No recent contacts found!")
        return
    
    # Always do a dry run first
    delete_contacts(recent_contacts, dry_run=True)
    
    if choice != "5":
        proceed = input(f"\nProceed with deleting {len(recent_contacts)} contacts? (y/N): ").strip().lower()
        if proceed == 'y':
            delete_contacts(recent_contacts, dry_run=False)
        else:
            print("❌ Deletion cancelled")

if __name__ == "__main__":
    main()
