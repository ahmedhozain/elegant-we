#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Migration Script for Elegant Immigration Services
This script migrates the database to support bilingual content and new features
"""

import sqlite3
from datetime import datetime

def migrate_database():
    """Main migration function"""
    conn = sqlite3.connect('website_content.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("Starting Database Migration...")
    print("=" * 60)
    
    # =========================================================================
    # STEP 1: Create new tables
    # =========================================================================
    
    print("\n[1/6] Creating 'services' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_ar TEXT NOT NULL,
            title_en TEXT NOT NULL,
            description_ar TEXT,
            description_en TEXT,
            icon TEXT,
            image_url TEXT,
            order_index INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Services table created successfully")
    
    print("\n[2/6] Creating 'about_sections' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS about_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_key TEXT NOT NULL UNIQUE,
            title_ar TEXT,
            title_en TEXT,
            content_ar TEXT,
            content_en TEXT,
            image_url TEXT,
            order_index INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ About sections table created successfully")
    
    print("\n[3/6] Creating 'contact_messages' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT,
            visa_type TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            replied_at TIMESTAMP
        )
    ''')
    print("✓ Contact messages table created successfully")
    
    print("\n[4/6] Creating 'contact_info' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            phone TEXT,
            whatsapp TEXT,
            address_ar TEXT,
            address_en TEXT,
            facebook TEXT,
            twitter TEXT,
            instagram TEXT,
            linkedin TEXT,
            youtube TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Contact info table created successfully")
    
    # =========================================================================
    # STEP 2: Modify stories table to support bilingual content
    # =========================================================================
    
    print("\n[5/6] Migrating 'stories' table to support bilingual content...")
    
    # Check if new columns already exist
    cursor.execute("PRAGMA table_info(stories)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'title_ar' not in columns:
        # Create new stories table with bilingual support
        print("  → Creating new bilingual stories table...")
        cursor.execute('''
            CREATE TABLE stories_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_ar TEXT NOT NULL,
                title_en TEXT NOT NULL,
                summary_ar TEXT,
                summary_en TEXT,
                content_ar TEXT NOT NULL,
                content_en TEXT NOT NULL,
                author_name_ar TEXT,
                author_name_en TEXT,
                story_date DATE,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migrate existing data
        print("  → Migrating existing stories data...")
        cursor.execute("SELECT * FROM stories")
        old_stories = cursor.fetchall()
        
        for story in old_stories:
            # old structure: id, name, title, content, image_url, created_at, updated_at
            story_id = story[0]
            name = story[1] if len(story) > 1 else 'Unknown'
            title = story[2] if len(story) > 2 else 'No Title'
            content = story[3] if len(story) > 3 else 'No Content'
            image_url = story[4] if len(story) > 4 else ''
            created_at = story[5] if len(story) > 5 else datetime.now()
            
            # Create summary (first 200 characters)
            summary = content[:200] + '...' if len(content) > 200 else content
            
            # Insert into new table (using same content for both languages initially)
            cursor.execute('''
                INSERT INTO stories_new 
                (id, title_ar, title_en, summary_ar, summary_en, content_ar, content_en, 
                 author_name_ar, author_name_en, story_date, image_url, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (story_id, title, title, summary, summary, content, content, 
                  name, name, created_at, image_url, created_at, datetime.now()))
        
        print(f"  → Migrated {len(old_stories)} stories successfully")
        
        # Drop old table and rename new one
        print("  → Replacing old stories table with new one...")
        cursor.execute("DROP TABLE stories")
        cursor.execute("ALTER TABLE stories_new RENAME TO stories")
        print("✓ Stories table migrated successfully")
    else:
        print("✓ Stories table already has bilingual support")
    
    # =========================================================================
    # STEP 3: Insert default data
    # =========================================================================
    
    print("\n[6/6] Inserting default data...")
    
    # Insert default services
    print("  → Inserting default services...")
    default_services = [
        ('تطبيق فيزا الزيارة والسياحة', 'Apply Visitor & Tourism Visa',
         'خدمات Elegant العامة تجعل زيارة كندا سهلة وخالية من التوتر. نساعدك في إعداد طلب الفيزا بكل احترافية.',
         'Elegant Public Services makes visiting Canada easy and stress-free. We help you prepare your visa application professionally.',
         'fa-plane-departure', '/static/images/service-img-1.webp', 1, 1),
        
        ('استشارات الهجرة', 'Immigration Consultancy',
         'نساعد العملاء في كندا للحصول على الإقامة الدائمة والجنسية وتصاريح الدراسة من خلال فريق متخصص.',
         'We help clients in Canada with permanent residency, citizenship, and study permits through our specialized team.',
         'fa-passport', '/static/images/service-img-2.webp', 2, 1),
        
        ('خدمات الاستقرار', 'Settlement Services',
         'خدمات الاستقرار تدعم الوافدين الجدد في كندا في الإسكان والوظائف والرعاية الصحية وأكثر.',
         'Settlement Services support newcomers in Canada with housing, jobs, healthcare, and more.',
         'fa-home', '/static/images/service-img-3.webp', 3, 1),
        
        ('تطبيق الهجرة للدراسة', 'Apply Study Immigration',
         'خدمات Elegant العامة تساعد في جعل أحلامك التعليمية الكندية حقيقة من خلال توفير كافة الدعم اللازم.',
         'Elegant Public Services helps make your Canadian education dreams a reality by providing all necessary support.',
         'fa-graduation-cap', '/static/images/service-img-4.webp', 4, 1),
        
        ('خدمات الترجمة المعتمدة', 'Certified Translation Services',
         'نقدم خدمات ترجمة معتمدة للوثائق الرسمية، مما يضمن قبولها من قبل السلطات الحكومية والمؤسسات التعليمية.',
         'We provide certified translation services for official documents, ensuring their acceptance by government authorities and educational institutions.',
         'fa-language', '/static/images/elegant-service-307.jpg', 5, 1),
    ]
    
    for service in default_services:
        cursor.execute('''
            INSERT OR IGNORE INTO services 
            (title_ar, title_en, description_ar, description_en, icon, image_url, order_index, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', service)
    print(f"  ✓ Inserted {len(default_services)} default services")
    
    # Insert default about sections
    print("  → Inserting default about sections...")
    default_about_sections = [
        ('company_intro', 'عن شركتنا', 'About Our Company',
         'خدمات Elegant العامة هي شركة هجرة كندية مسجلة تحت سلطات التسجيل الحكومية الفيدرالية والإقليمية لكندا. نحن نقدم خدمات هجرة شاملة ومهنية لمساعدة عملائنا في تحقيق أحلامهم.',
         'Elegant Public Services is a registered Canadian Immigration firm under the Federal and Provincial Government of Canada\'s registry authorities. We provide comprehensive and professional immigration services to help our clients achieve their dreams.',
         '/static/images/about-team.webp', 1, 1),
        
        ('our_team', 'فريقنا المميز', 'Our Special Team',
         'خدمات Elegant توفر إرشاداً متخصصاً ودعماً شاملاً للهجرة إلى كندا، مستفيدة من فريقها المهني وشركائها الموثوقين لضمان عملية سلسة وناجحة.',
         'Elegant Services provides expert guidance and comprehensive support for migrating to Canada, leveraging their professional team and trusted partners to ensure a smooth and successful process.',
         '/static/images/about-service.webp', 2, 1),
        
        ('client_focus', 'أكثر من مجرد عميل', 'More Than Just A Client',
         'نقدر كل عميل كفرد، ونقدم خدمة شخصية وموثوقة تحترم احتياجاتك وتضمن التعامل مع قضيتك بعناية ومهنية.',
         'We value every client as an individual, providing personalized, trustworthy service that respects your needs and ensures your case is handled with care and professionalism.',
         '/static/images/about-client.webp', 3, 1),
        
        ('beyond_services', 'ما بعد الخدمات', 'Beyond The Services',
         'نتجاوز الخدمات من خلال تقديم التعاطف والدعم والطمأنينة، وبناء علاقات قوية مع العملاء. شعارنا: "يمكنك الاعتماد علينا طوال عملية الهجرة."',
         'We go beyond services by offering empathy, support, and reassurance, building strong relationships with clients. Our motto: "You can rely on us throughout the immigration process."',
         '', 4, 1),
    ]
    
    for section in default_about_sections:
        cursor.execute('''
            INSERT OR IGNORE INTO about_sections 
            (section_key, title_ar, title_en, content_ar, content_en, image_url, order_index, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', section)
    print(f"  ✓ Inserted {len(default_about_sections)} default about sections")
    
    # Insert default contact info
    print("  → Inserting default contact info...")
    cursor.execute('''
        INSERT OR IGNORE INTO contact_info 
        (id, email, phone, whatsapp, address_ar, address_en, facebook, twitter, instagram, linkedin)
        VALUES (1, 'info@elegantservices.ca', '+1 (123) 456-7890', '+1 (123) 456-7890',
                'تورونتو، أونتاريو، كندا', 'Toronto, Ontario, Canada',
                'https://facebook.com/elegantservices', 
                'https://twitter.com/elegantservices',
                'https://instagram.com/elegantservices',
                'https://linkedin.com/company/elegantservices')
    ''')
    print("  ✓ Inserted default contact info")
    
    # Commit all changes
    conn.commit()
    
    # =========================================================================
    # Display summary
    # =========================================================================
    
    print("\n" + "=" * 60)
    print("Migration Summary:")
    print("=" * 60)
    
    # Count records in each table
    cursor.execute("SELECT COUNT(*) FROM services")
    services_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM about_sections")
    about_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_messages")
    messages_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contact_info")
    contact_info_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM stories")
    stories_count = cursor.fetchone()[0]
    
    print(f"✓ Services: {services_count} records")
    print(f"✓ About Sections: {about_count} records")
    print(f"✓ Contact Messages: {messages_count} records")
    print(f"✓ Contact Info: {contact_info_count} records")
    print(f"✓ Stories: {stories_count} records (with bilingual support)")
    
    print("\n" + "=" * 60)
    print("✓ Database Migration Completed Successfully!")
    print("=" * 60)
    
    conn.close()

if __name__ == '__main__':
    try:
        migrate_database()
    except Exception as e:
        print(f"\n✗ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()

