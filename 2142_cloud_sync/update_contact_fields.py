#!/usr/bin/env python3
"""
Script to update the contact_messages table with new fields
Run this script to migrate existing database to the new schema
"""

import sqlite3
import os

def update_database():
    db_path = 'website_content.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        return
    
    print("🔄 Starting database update...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("PRAGMA table_info(contact_messages)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Current columns: {', '.join(columns)}")
        
        # Add phone column if it doesn't exist
        if 'phone' not in columns:
            print("➕ Adding 'phone' column...")
            cursor.execute('ALTER TABLE contact_messages ADD COLUMN phone TEXT')
            print("✅ Phone column added successfully")
        else:
            print("ℹ️  Phone column already exists")
        
        # Add governorate column if it doesn't exist
        if 'governorate' not in columns:
            print("➕ Adding 'governorate' column...")
            cursor.execute('ALTER TABLE contact_messages ADD COLUMN governorate TEXT')
            print("✅ Governorate column added successfully")
        else:
            print("ℹ️  Governorate column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the update
        cursor.execute("PRAGMA table_info(contact_messages)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"\n✅ Updated columns: {', '.join(new_columns)}")
        
        conn.close()
        
        print("\n🎉 Database updated successfully!")
        print("\n📝 Note: The old 'company' and 'visa_type' columns are preserved for backward compatibility.")
        print("   You can manually remove them later if needed using:")
        print("   - ALTER TABLE contact_messages DROP COLUMN company;")
        print("   - ALTER TABLE contact_messages DROP COLUMN visa_type;")
        
    except sqlite3.Error as e:
        print(f"❌ Error updating database: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return

if __name__ == '__main__':
    print("=" * 60)
    print("📊 Contact Form Fields Update Script")
    print("=" * 60)
    print("\nThis script will update your database with the new contact form fields:")
    print("  - Adds: phone, governorate")
    print("  - Old fields (company, visa_type) remain for backward compatibility")
    print()
    
    response = input("Do you want to continue? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        update_database()
    else:
        print("❌ Update cancelled.")

