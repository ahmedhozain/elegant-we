from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure random key

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_VIDEO_SIZE

# Create upload folders if they don't exist
os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'images'), exist_ok=True)

def allowed_file(filename, file_type='video'):
    if file_type == 'video':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
    elif file_type == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    return False

# Language support
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'ar': 'العربية'
}

def get_language():
    return session.get('language', 'en')

def set_language(lang):
    if lang in SUPPORTED_LANGUAGES:
        session['language'] = lang

# Database initialization
def init_db():
    conn = sqlite3.connect('website_content.db')
    cursor = conn.cursor()
    
    # Create stories table with bilingual support
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stories (
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
            video_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if video_path column exists, if not add it
    cursor.execute("PRAGMA table_info(stories)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'video_path' not in columns:
        try:
            cursor.execute('ALTER TABLE stories ADD COLUMN video_path TEXT')
            print("✅ Added video_path column to stories table")
        except sqlite3.OperationalError:
            pass  # Column already exists
    
    # Create services table
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
    
    # Create about_sections table
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
    
    # Create contact_messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            governorate TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            replied_at TIMESTAMP
        )
    ''')
    
    # Check if phone and governorate columns exist, if not add them
    cursor.execute("PRAGMA table_info(contact_messages)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'phone' not in columns:
        try:
            cursor.execute('ALTER TABLE contact_messages ADD COLUMN phone TEXT')
            print("✅ Added phone column to contact_messages table")
        except sqlite3.OperationalError:
            pass
    if 'governorate' not in columns:
        try:
            cursor.execute('ALTER TABLE contact_messages ADD COLUMN governorate TEXT')
            print("✅ Added governorate column to contact_messages table")
        except sqlite3.OperationalError:
            pass
    
    # Create contact_info table
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
    
    # Create site content table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            title_en TEXT,
            title_ar TEXT,
            content_en TEXT,
            content_ar TEXT,
            image_url TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create page sections table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            section_key TEXT NOT NULL,
            title_en TEXT,
            title_ar TEXT,
            content_en TEXT,
            content_ar TEXT,
            image_url TEXT,
            order_index INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(page_name, section_key)
        )
    ''')
    
    # Insert default content
    default_sections = [
        ('index', 'hero_title', 'Elegant - Your Gate for a Better Future', 'Elegant - بوابتك لمستقبل أفضل', 
         'A Simple Approach to the Immigration Process. Professional guidance and support to help you achieve your dreams of living and working abroad.',
         'نهج بسيط لعملية الهجرة. إرشاد مهني ودعم لمساعدتك في تحقيق أحلامك في العيش والعمل في الخارج.', '', 1),
        ('index', 'hero_subtitle', 'Start Your Journey', 'ابدأ رحلتك', '', '', '', 2),
        ('index', 'services_title', 'Your Path to a New Beginning', 'طريقك نحو بداية جديدة',
         'Comprehensive immigration services designed to make your journey smooth and successful',
         'خدمات الهجرة الشاملة المصممة لجعل رحلتك سلسة وناجحة', '', 3),
        ('index', 'about_title', 'Success Stories', 'قصص النجاح',
         'Since 2018, we\'ve been helping people achieve their dreams of living, working, and studying abroad.',
         'منذ عام 2018، نساعد الناس في تحقيق أحلامهم في العيش والعمل والدراسة في الخارج.', '', 4),
        ('index', 'contact_title', 'Start Your Immigration Journey Today', 'ابدأ رحلة الهجرة اليوم',
         'Ready to take the first step? Contact us for a free consultation and let\'s discuss your immigration goals.',
         'مستعد لاتخاذ الخطوة الأولى؟ تواصل معنا للحصول على استشارة مجانية ودعنا نناقش أهدافك في الهجرة.', '', 5),
        
        # Navigation translations
        ('index', 'nav_home', 'Home', 'الرئيسية', '', '', '', 10),
        ('index', 'nav_services', 'Services', 'الخدمات', '', '', '', 11),
        ('index', 'nav_about', 'About Us', 'من نحن', '', '', '', 12),
        ('index', 'nav_stories', 'Stories', 'القصص', '', '', '', 13),
        ('index', 'nav_contact', 'Contact', 'تواصل معنا', '', '', '', 14),
        ('index', 'nav_dashboard', 'Dashboard', 'لوحة التحكم', '', '', '', 15),
        
        # Main services section
        ('index', 'main_services_title', 'Our Main Services', 'خدماتنا الرئيسية', 
         'We offer complete visa and immigration solutions — from visitor and study visas to expert consultancy and settlement support — ensuring a smooth, guided, and stress-free process for travel, study, and relocation abroad.',
         'نقدم حلول شاملة للفيزا والهجرة — من فيزا الزيارة والدراسة إلى الاستشارات المتخصصة ودعم الاستقرار — مما يضمن عملية سلسة ومرشدة وخالية من التوتر للسفر والدراسة والانتقال للخارج.', '', 20),
        ('index', 'visitor_visa_text', 'Apply Visitor & Tourism Visa', 'تطبيق فيزا الزيارة والسياحة', '', '', '', 21),
        ('index', 'immigration_consultancy_text', 'Immigration Consultancy', 'استشارات الهجرة', '', '', '', 22),
        ('index', 'settlement_services_text', 'Settlement Services', 'خدمات الاستقرار', '', '', '', 23),
        ('index', 'study_immigration_text', 'Apply Study Immigration', 'تطبيق الهجرة للدراسة', '', '', '', 24),
        ('index', 'explore_more_text', 'Explore More →', 'استكشف المزيد ←', '', '', '', 25),
        
        # Translation services section
        ('index', 'translation_title', 'Certified Translation Services', 'خدمات الترجمة المعتمدة',
         'We provide certified translation services for official documents, ensuring they are accepted by government authorities, educational institutions, and international organizations with accuracy and professionalism.',
         'نقدم خدمات ترجمة معتمدة للوثائق الرسمية، مما يضمن قبولها من قبل السلطات الحكومية والمؤسسات التعليمية والمنظمات الدولية بدقة ومهنية.', '', 30),
        ('index', 'translate_docs_text', 'Translate official documents like certificates and records.', 'ترجمة الوثائق الرسمية مثل الشهادات والسجلات.', '', '', '', 31),
        ('index', 'ensure_recognition_text', 'Ensure recognition by authorities and institutions.', 'ضمان الاعتراف من قبل السلطات والمؤسسات.', '', '', '', 32),
        ('index', 'maintain_accuracy_text', 'Maintain accuracy and clarity.', 'الحفاظ على الدقة والوضوح.', '', '', '', 33),
        ('index', 'fast_delivery_text', 'Provide fast, certified delivery.', 'تقديم تسليم سريع ومعتمد.', '', '', '', 34),
        
        # Service cards descriptions
        ('index', 'visitor_visa_desc', 'Elegant Public Services makes visiting Canada easy and stress-free.', 'خدمات Elegant العامة تجعل زيارة كندا سهلة وخالية من التوتر.', '', '', '', 40),
        ('index', 'immigration_consultancy_desc', 'We help clients in Canada with permanent residency, citizenship, and study permits.', 'نساعد العملاء في كندا للحصول على الإقامة الدائمة والجنسية وتصاريح الدراسة.', '', '', '', 41),
        ('index', 'settlement_services_desc', 'Settlement Services support newcomers in Canada with housing, jobs, and healthcare.', 'خدمات الاستقرار تدعم الوافدين الجدد في كندا في الإسكان والوظائف والرعاية الصحية.', '', '', '', 42),
        ('index', 'study_immigration_desc', 'Elegant Public Services helps make your Canadian education dreams a reality.', 'خدمات Elegant العامة تساعد في جعل أحلامك التعليمية الكندية حقيقة.', '', '', '', 43),
        
        # Why Choose Us section
        ('index', 'why_choose_us_title', 'Why Choose Us?', 'لماذا تختارنا؟',
         'Elegant Public Services is a registered Canadian Immigration firm under the Federal and Provincial Government of Canada\'s registry authorities.',
         'خدمات Elegant العامة هي شركة هجرة كندية مسجلة تحت سلطات التسجيل الحكومية الفيدرالية والإقليمية لكندا.', '', 50),
        ('index', 'our_team_title', 'Our Team Makes Us Special', 'فريقنا يجعلنا مميزين',
         'Elegant Services provides expert guidance and comprehensive support for migrating to Canada, leveraging their professional team and trusted partners to ensure a smooth and successful process.',
         'خدمات Elegant توفر إرشاداً متخصصاً ودعماً شاملاً للهجرة إلى كندا، مستفيدة من فريقها المهني وشركائها الموثوقين لضمان عملية سلسة وناجحة.', '', 51),
        ('index', 'more_than_client_title', 'More Than Just A Client', 'أكثر من مجرد عميل',
         'We value every client as an individual, providing personalized, trustworthy service that respects your needs and ensures your case is handled with care and professionalism.',
         'نقدر كل عميل كفرد، ونقدم خدمة شخصية وموثوقة تحترم احتياجاتك وتضمن التعامل مع قضيتك بعناية ومهنية.', '', 52),
        ('index', 'beyond_services_title', 'Beyond The Services', 'ما بعد الخدمات',
         'We go beyond services by offering empathy, support, and reassurance, building strong relationships with clients. Our motto: "You can rely on us throughout the immigration process."',
         'نتجاوز الخدمات من خلال تقديم التعاطف والدعم والطمأنينة، وبناء علاقات قوية مع العملاء. شعارنا: "يمكنك الاعتماد علينا طوال عملية الهجرة."', '', 53),
        ('index', 'read_more_title', 'Read More About Us', 'اقرأ المزيد عنا',
         'Click to learn more about our story, values, and what makes us special.',
         'انقر لمعرفة المزيد عن قصتنا وقيمنا وما يجعلنا مميزين.', '', 54),
        
        # Contact form section
        ('index', 'consultation_title', 'Request a Consultation', 'طلب استشارة',
         'Fill out the form below and our immigration consultant will contact you within 24 hours.',
         'املأ النموذج أدناه وسيتواصل معك مستشار الهجرة الخاص بنا خلال 24 ساعة.', '', 60),
        ('index', 'full_name_label', 'Full Name', 'الاسم الكامل', '', '', '', 61),
        ('index', 'email_label', 'Email Address', 'عنوان البريد الإلكتروني', '', '', '', 62),
        ('index', 'company_label', 'Company Name', 'اسم الشركة', '', '', '', 63),
        ('index', 'visa_type_label', 'What type of visa are you interested in?', 'ما نوع الفيزا التي تهتم بها؟', '', '', '', 64),
        ('index', 'select_visa_option', 'Select a Visa Type', 'اختر نوع الفيزا', '', '', '', 65),
        ('index', 'work_visa_option', 'Work Visa', 'فيزا العمل', '', '', '', 66),
        ('index', 'study_visa_option', 'Study Visa', 'فيزا الدراسة', '', '', '', 67),
        ('index', 'family_visa_option', 'Family/Spouse Visa', 'فيزا العائلة/الزوج', '', '', '', 68),
        ('index', 'business_visa_option', 'Business/Investor Visa', 'فيزا الأعمال/المستثمر', '', '', '', 69),
        ('index', 'permanent_option', 'Permanent Residency', 'الإقامة الدائمة', '', '', '', 70),
        ('index', 'other_option', 'Other', 'أخرى', '', '', '', 71),
        ('index', 'goals_label', 'Tell us about your immigration goals', 'أخبرنا عن أهدافك في الهجرة', '', '', '', 72),
        ('index', 'goals_placeholder', 'Share your plans, destination country, timeline, and any questions you have...', 'شارك خططك وبلد الوجهة والجدول الزمني وأي أسئلة لديك...', '', '', '', 73),
        ('index', 'submit_button', 'Request Free Consultation', 'طلب استشارة مجانية', '', '', '', 74),
        
        # Quick contact section
        ('index', 'quick_contact_title', 'Quick Contact', 'التواصل السريع', '', '', '', 80),
        ('index', 'email_us_title', 'Email Us', 'راسلنا', '', '', '', 81),
        ('index', 'live_chat_title', 'Live Chat', 'الدردشة المباشرة', '', '', '', 82),
        ('index', 'live_chat_hours', 'Available 9AM-6PM EST', 'متاح من 9 صباحاً إلى 6 مساءً بتوقيت شرق أمريكا', '', '', '', 83),
        ('index', 'call_us_title', 'Call Us', 'اتصل بنا', '', '', '', 84),
        
        # Office locations
        ('index', 'our_offices_title', 'Our Offices', 'مكاتبنا', '', '', '', 90),
        ('index', 'sf_office', 'San Francisco', 'سان فرانسيسكو', '', '', '', 91),
        ('index', 'london_office', 'London', 'لندن', '', '', '', 92),
        ('index', 'singapore_office', 'Singapore', 'سنغافورة', '', '', '', 93),
        
        # Stories section
        ('index', 'no_stories_text', 'No stories yet', 'لا توجد قصص بعد',
         'We will soon add our clients\' success stories', 'سنضيف قريباً قصص نجاح عملائنا', '', 100),
        ('index', 'manage_stories_text', 'Manage Stories', 'إدارة القصص',
         'To add new stories or manage content', 'لإضافة قصص جديدة أو إدارة المحتوى', '', 101),
        ('index', 'read_full_story_text', 'اقرأ القصة كاملة →', 'Read Full Story →', '', '', '', 102),
        ('index', 'by_text', 'بواسطة:', 'By:', '', '', '', 103),
        
        # About text
        ('index', 'about_description', 'At Elegant Public Services, we offer dedicated, compassionate, and expert support, combining deep knowledge with unwavering commitment. We empower our clients with confidence, guidance, and reassurance, ensuring they feel fully supported, understood, and confident throughout every stage of their immigration journey.', 'في خدمات Elegant العامة، نقدم دعماً مخصصاً ومتعاطفاً ومتخصصاً، نجمع بين المعرفة العميقة والالتزام الثابت. نمكن عملاءنا بالثقة والإرشاد والطمأنينة، مما يضمن شعورهم بالدعم الكامل والفهم والثقة في كل مرحلة من رحلة الهجرة.', '', '', '', 110),
        
        # Form placeholders
        ('index', 'name_placeholder', 'John Doe', 'أحمد محمد', '', '', '', 120),
        ('index', 'email_placeholder', 'john@example.com', 'ahmed@example.com', '', '', '', 121),
        ('index', 'phone_label', 'Phone Number', 'رقم الهاتف', '', '', '', 122),
        ('index', 'phone_placeholder', '+1 234 567 8900', '+20 123 456 7890', '', '', '', 123),
        ('index', 'governorate_label', 'Governorate / State', 'المحافظة', '', '', '', 124),
        ('index', 'governorate_placeholder', 'Select your governorate', 'اختر محافظتك', '', '', '', 125),
        ('index', 'notes_label', 'Notes', 'ملاحظات', '', '', '', 126)
    ]
    
    for section in default_sections:
        # Ensure each section has exactly 8 elements
        if len(section) != 8:
            print(f"Warning: Section {section[1]} has {len(section)} elements, expected 8. Skipping...")
            continue
        cursor.execute('''
            INSERT OR IGNORE INTO page_sections 
            (page_name, section_key, title_en, title_ar, content_en, content_ar, image_url, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', section)
    
    conn.commit()
    
    # Insert default services if table is empty
    cursor.execute('SELECT COUNT(*) FROM services')
    if cursor.fetchone()[0] == 0:
        default_services = [
            ('تطبيق فيزا الزيارة والسياحة', 'Apply Visitor & Tourism Visa',
             'خدمات Elegant العامة تجعل زيارة كندا سهلة وخالية من التوتر.', 
             'Elegant Public Services makes visiting Canada easy and stress-free.',
             'fa-plane-departure', '/static/images/service-img-1.webp', 1, 1),
            ('استشارات الهجرة', 'Immigration Consultancy',
             'نساعد العملاء في كندا للحصول على الإقامة الدائمة والجنسية وتصاريح الدراسة.',
             'We help clients in Canada with permanent residency, citizenship, and study permits.',
             'fa-passport', '/static/images/service-img-2.webp', 2, 1),
            ('خدمات الاستقرار', 'Settlement Services',
             'خدمات الاستقرار تدعم الوافدين الجدد في كندا في الإسكان والوظائف والرعاية الصحية.',
             'Settlement Services support newcomers in Canada with housing, jobs, and healthcare.',
             'fa-home', '/static/images/service-img-3.webp', 3, 1),
            ('تطبيق الهجرة للدراسة', 'Apply Study Immigration',
             'خدمات Elegant العامة تساعد في جعل أحلامك التعليمية الكندية حقيقة.',
             'Elegant Public Services helps make your Canadian education dreams a reality.',
             'fa-graduation-cap', '/static/images/service-img-4.webp', 4, 1),
        ]
        for service in default_services:
            cursor.execute('''
                INSERT INTO services (title_ar, title_en, description_ar, description_en, icon, image_url, order_index, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', service)
        conn.commit()
    
    # Insert default about sections if table is empty
    cursor.execute('SELECT COUNT(*) FROM about_sections')
    if cursor.fetchone()[0] == 0:
        default_about = [
            ('company_intro', 'عن شركتنا', 'About Our Company',
             'خدمات Elegant العامة هي شركة هجرة كندية مسجلة تحت سلطات التسجيل الحكومية.', 
             'Elegant Public Services is a registered Canadian Immigration firm.',
             '/static/images/about-team.webp', 1, 1),
        ]
        for section in default_about:
            cursor.execute('''
                INSERT INTO about_sections (section_key, title_ar, title_en, content_ar, content_en, image_url, order_index, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', section)
        conn.commit()
    
    # Insert default contact info if table is empty
    cursor.execute('SELECT COUNT(*) FROM contact_info')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO contact_info (email, phone, whatsapp, address_ar, address_en)
            VALUES ('info@elegantservices.ca', '+1 (123) 456-7890', '+1 (123) 456-7890',
                    'تورونتو، أونتاريو، كندا', 'Toronto, Ontario, Canada')
        ''')
        conn.commit()
    
    conn.close()

# Initialize database on startup
init_db()

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('website_content.db')
    conn.row_factory = sqlite3.Row
    return conn

# Language switching route
@app.route('/set_language/<lang>')
def set_language_route(lang):
    set_language(lang)
    return redirect(request.referrer or url_for('index'))

# Route for the home page
@app.route('/')
def index():
    # Get stories and content from database
    conn = get_db_connection()
    stories = conn.execute('SELECT * FROM stories ORDER BY created_at DESC').fetchall()
    sections = conn.execute('''
        SELECT * FROM page_sections 
        WHERE page_name = 'index' 
        ORDER BY order_index ASC
    ''').fetchall()
    conn.close()
    current_lang = get_language()
    return render_template('index.html', stories=stories, sections=sections, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

# Route for services page
@app.route('/services')
def services():
    current_lang = get_language()
    conn = get_db_connection()
    sections = conn.execute('''
        SELECT * FROM page_sections 
        WHERE page_name = 'index' 
        ORDER BY order_index ASC
    ''').fetchall()
    services_list = conn.execute('SELECT * FROM services WHERE is_active = 1 ORDER BY order_index ASC').fetchall()
    conn.close()
    return render_template('services.html', current_lang=current_lang, languages=SUPPORTED_LANGUAGES, sections=sections, services=services_list)

# Route for pricing page
@app.route('/pricing')
def pricing():
    return render_template('index.html', section='pricing')

# Route for about page
@app.route('/about')
def about():
    current_lang = get_language()
    conn = get_db_connection()
    sections = conn.execute('''
        SELECT * FROM page_sections 
        WHERE page_name = 'index' 
        ORDER BY order_index ASC
    ''').fetchall()
    about_sections = conn.execute('SELECT * FROM about_sections WHERE is_active = 1 ORDER BY order_index ASC').fetchall()
    conn.close()
    return render_template('about.html', current_lang=current_lang, languages=SUPPORTED_LANGUAGES, sections=sections, about_sections=about_sections)

# Route for contact page
@app.route('/contact')
def contact():
    return render_template('index.html', section='contact')

# Dashboard routes
@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    stories_count = conn.execute('SELECT COUNT(*) as count FROM stories').fetchone()['count']
    services_count = conn.execute('SELECT COUNT(*) as count FROM services WHERE is_active = 1').fetchone()['count']
    about_count = conn.execute('SELECT COUNT(*) as count FROM about_sections WHERE is_active = 1').fetchone()['count']
    unread_messages = conn.execute('SELECT COUNT(*) as count FROM contact_messages WHERE is_read = 0').fetchone()['count']
    total_messages = conn.execute('SELECT COUNT(*) as count FROM contact_messages').fetchone()['count']
    
    # Get latest messages
    latest_messages = conn.execute('''
        SELECT * FROM contact_messages 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    current_lang = get_language()
    return render_template('dashboard.html', 
                         stories_count=stories_count,
                         services_count=services_count,
                         about_count=about_count,
                         unread_messages=unread_messages,
                         total_messages=total_messages,
                         latest_messages=latest_messages,
                         current_lang=current_lang, 
                         languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/stories')
def dashboard_stories():
    conn = get_db_connection()
    stories = conn.execute('SELECT * FROM stories ORDER BY created_at DESC').fetchall()
    conn.close()
    current_lang = get_language()
    return render_template('dashboard_stories.html', stories=stories, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/stories/add', methods=['GET', 'POST'])
def add_story():
    if request.method == 'POST':
        title_ar = request.form['title_ar']
        title_en = request.form['title_en']
        summary_ar = request.form.get('summary_ar', '')
        summary_en = request.form.get('summary_en', '')
        content_ar = request.form['content_ar']
        content_en = request.form['content_en']
        author_name_ar = request.form.get('author_name_ar', '')
        author_name_en = request.form.get('author_name_en', '')
        story_date = request.form.get('story_date', datetime.now().strftime('%Y-%m-%d'))
        image_url = request.form.get('image_url', '')
        
        # Handle video upload
        video_path = None
        if 'video_file' in request.files:
            video_file = request.files['video_file']
            if video_file and video_file.filename != '' and allowed_file(video_file.filename, 'video'):
                filename = secure_filename(video_file.filename)
                # Add timestamp to make filename unique
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename))
                video_path = f"/static/uploads/videos/{filename}"
        
        # Handle image upload
        if 'image_file' in request.files:
            image_file = request.files['image_file']
            if image_file and image_file.filename != '' and allowed_file(image_file.filename, 'image'):
                filename = secure_filename(image_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'images', filename))
                image_url = f"/static/uploads/images/{filename}"
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO stories 
            (title_ar, title_en, summary_ar, summary_en, content_ar, content_en, 
             author_name_ar, author_name_en, story_date, image_url, video_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title_ar, title_en, summary_ar, summary_en, content_ar, content_en,
              author_name_ar, author_name_en, story_date, image_url, video_path))
        conn.commit()
        conn.close()
        
        current_lang = get_language()
        if current_lang == 'ar':
            flash('تم إضافة القصة بنجاح!', 'success')
        else:
            flash('Story added successfully!', 'success')
        return redirect(url_for('dashboard_stories'))
    
    current_lang = get_language()
    return render_template('add_story.html', current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/stories/edit/<int:story_id>', methods=['GET', 'POST'])
def edit_story(story_id):
    conn = get_db_connection()
    current_lang = get_language()
    
    if request.method == 'POST':
        title_ar = request.form['title_ar']
        title_en = request.form['title_en']
        summary_ar = request.form.get('summary_ar', '')
        summary_en = request.form.get('summary_en', '')
        content_ar = request.form['content_ar']
        content_en = request.form['content_en']
        author_name_ar = request.form.get('author_name_ar', '')
        author_name_en = request.form.get('author_name_en', '')
        story_date = request.form.get('story_date', '')
        image_url = request.form.get('image_url', '')
        
        # Get existing story to check for existing video
        story = conn.execute('SELECT video_path FROM stories WHERE id = ?', (story_id,)).fetchone()
        video_path = story['video_path'] if story else None
        
        # Handle video upload
        if 'video_file' in request.files:
            video_file = request.files['video_file']
            if video_file and video_file.filename != '' and allowed_file(video_file.filename, 'video'):
                # Delete old video if exists
                if video_path:
                    old_video_path = video_path.lstrip('/')
                    if os.path.exists(old_video_path):
                        os.remove(old_video_path)
                
                filename = secure_filename(video_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename))
                video_path = f"/static/uploads/videos/{filename}"
        
        # Handle image upload
        if 'image_file' in request.files:
            image_file = request.files['image_file']
            if image_file and image_file.filename != '' and allowed_file(image_file.filename, 'image'):
                filename = secure_filename(image_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'images', filename))
                image_url = f"/static/uploads/images/{filename}"
        
        conn.execute('''
            UPDATE stories 
            SET title_ar = ?, title_en = ?, summary_ar = ?, summary_en = ?, 
                content_ar = ?, content_en = ?, author_name_ar = ?, author_name_en = ?,
                story_date = ?, image_url = ?, video_path = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (title_ar, title_en, summary_ar, summary_en, content_ar, content_en,
              author_name_ar, author_name_en, story_date, image_url, video_path, story_id))
        conn.commit()
        conn.close()
        
        if current_lang == 'ar':
            flash('تم تحديث القصة بنجاح!', 'success')
        else:
            flash('Story updated successfully!', 'success')
        return redirect(url_for('dashboard_stories'))
    
    story = conn.execute('SELECT * FROM stories WHERE id = ?', (story_id,)).fetchone()
    conn.close()
    
    if story is None:
        if current_lang == 'ar':
            flash('القصة غير موجودة!', 'error')
        else:
            flash('Story not found!', 'error')
        return redirect(url_for('dashboard_stories'))
    
    return render_template('edit_story.html', story=story, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/stories/delete/<int:story_id>')
def delete_story(story_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM stories WHERE id = ?', (story_id,))
    conn.commit()
    conn.close()
    
    current_lang = get_language()
    if current_lang == 'ar':
        flash('تم حذف القصة بنجاح!', 'success')
    else:
        flash('Story deleted successfully!', 'success')
    return redirect(url_for('dashboard_stories'))

@app.route('/story/<int:story_id>')
def view_story(story_id):
    conn = get_db_connection()
    story = conn.execute('SELECT * FROM stories WHERE id = ?', (story_id,)).fetchone()
    sections = conn.execute('SELECT * FROM page_sections WHERE page_name = "index"').fetchall()
    conn.close()
    
    if story is None:
        current_lang = get_language()
        if current_lang == 'ar':
            flash('القصة غير موجودة!', 'error')
        else:
            flash('Story not found!', 'error')
        return redirect(url_for('index'))
    
    current_lang = get_language()
    return render_template('story_detail.html', story=story, sections=sections, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

# Stories page - view all stories
@app.route('/stories')
def stories_page():
    conn = get_db_connection()
    stories = conn.execute('SELECT * FROM stories ORDER BY created_at DESC').fetchall()
    sections = conn.execute('SELECT * FROM page_sections WHERE page_name = "index"').fetchall()
    conn.close()
    current_lang = get_language()
    return render_template('stories_page.html', stories=stories, sections=sections, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

# Content Management Routes
@app.route('/dashboard/content')
def dashboard_content():
    conn = get_db_connection()
    sections = conn.execute('''
        SELECT * FROM page_sections 
        WHERE page_name = 'index' 
        ORDER BY order_index ASC
    ''').fetchall()
    conn.close()
    current_lang = get_language()
    return render_template('dashboard_content.html', sections=sections, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/content/edit/<int:section_id>', methods=['GET', 'POST'])
def edit_content(section_id):
    conn = get_db_connection()
    current_lang = get_language()
    
    if request.method == 'POST':
        title_en = request.form.get('title_en', '')
        title_ar = request.form.get('title_ar', '')
        content_en = request.form.get('content_en', '')
        content_ar = request.form.get('content_ar', '')
        image_url = request.form.get('image_url', '')
        
        conn.execute('''
            UPDATE page_sections 
            SET title_en = ?, title_ar = ?, content_en = ?, content_ar = ?, image_url = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title_en, title_ar, content_en, content_ar, image_url, section_id))
        conn.commit()
        conn.close()
        
        if current_lang == 'ar':
            flash('تم تحديث المحتوى بنجاح!', 'success')
        else:
            flash('Content updated successfully!', 'success')
        return redirect(url_for('dashboard_content'))
    
    section = conn.execute('SELECT * FROM page_sections WHERE id = ?', (section_id,)).fetchone()
    conn.close()
    
    if section is None:
        if current_lang == 'ar':
            flash('القسم غير موجود!', 'error')
        else:
            flash('Section not found!', 'error')
        return redirect(url_for('dashboard_content'))
    
    return render_template('edit_content.html', section=section, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

# ============================================================================
# SERVICES MANAGEMENT ROUTES
# ============================================================================

@app.route('/dashboard/services')
def dashboard_services():
    conn = get_db_connection()
    services = conn.execute('SELECT * FROM services ORDER BY order_index ASC').fetchall()
    conn.close()
    current_lang = get_language()
    return render_template('dashboard_services.html', services=services, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/services/add', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        title_ar = request.form['title_ar']
        title_en = request.form['title_en']
        description_ar = request.form.get('description_ar', '')
        description_en = request.form.get('description_en', '')
        icon = request.form.get('icon', 'fa-star')
        image_url = request.form.get('image_url', '')
        order_index = request.form.get('order_index', 0)
        is_active = 1 if request.form.get('is_active') == 'on' else 0
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO services 
            (title_ar, title_en, description_ar, description_en, icon, image_url, order_index, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title_ar, title_en, description_ar, description_en, icon, image_url, order_index, is_active))
        conn.commit()
        conn.close()
        
        current_lang = get_language()
        if current_lang == 'ar':
            flash('تم إضافة الخدمة بنجاح!', 'success')
        else:
            flash('Service added successfully!', 'success')
        return redirect(url_for('dashboard_services'))
    
    current_lang = get_language()
    return render_template('add_service.html', current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/services/edit/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    conn = get_db_connection()
    current_lang = get_language()
    
    if request.method == 'POST':
        title_ar = request.form['title_ar']
        title_en = request.form['title_en']
        description_ar = request.form.get('description_ar', '')
        description_en = request.form.get('description_en', '')
        icon = request.form.get('icon', 'fa-star')
        image_url = request.form.get('image_url', '')
        order_index = request.form.get('order_index', 0)
        is_active = 1 if request.form.get('is_active') == 'on' else 0
        
        conn.execute('''
            UPDATE services 
            SET title_ar = ?, title_en = ?, description_ar = ?, description_en = ?,
                icon = ?, image_url = ?, order_index = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title_ar, title_en, description_ar, description_en, icon, image_url, order_index, is_active, service_id))
        conn.commit()
        conn.close()
        
        if current_lang == 'ar':
            flash('تم تحديث الخدمة بنجاح!', 'success')
        else:
            flash('Service updated successfully!', 'success')
        return redirect(url_for('dashboard_services'))
    
    service = conn.execute('SELECT * FROM services WHERE id = ?', (service_id,)).fetchone()
    conn.close()
    
    if service is None:
        if current_lang == 'ar':
            flash('الخدمة غير موجودة!', 'error')
        else:
            flash('Service not found!', 'error')
        return redirect(url_for('dashboard_services'))
    
    return render_template('edit_service.html', service=service, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/services/delete/<int:service_id>')
def delete_service(service_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM services WHERE id = ?', (service_id,))
    conn.commit()
    conn.close()
    
    current_lang = get_language()
    if current_lang == 'ar':
        flash('تم حذف الخدمة بنجاح!', 'success')
    else:
        flash('Service deleted successfully!', 'success')
    return redirect(url_for('dashboard_services'))

@app.route('/dashboard/services/toggle/<int:service_id>')
def toggle_service(service_id):
    conn = get_db_connection()
    service = conn.execute('SELECT is_active FROM services WHERE id = ?', (service_id,)).fetchone()
    if service:
        new_status = 0 if service['is_active'] else 1
        conn.execute('UPDATE services SET is_active = ? WHERE id = ?', (new_status, service_id))
        conn.commit()
    conn.close()
    return redirect(url_for('dashboard_services'))

# ============================================================================
# ABOUT US MANAGEMENT ROUTES
# ============================================================================

@app.route('/dashboard/about')
def dashboard_about():
    conn = get_db_connection()
    sections = conn.execute('SELECT * FROM about_sections ORDER BY order_index ASC').fetchall()
    conn.close()
    current_lang = get_language()
    return render_template('dashboard_about.html', sections=sections, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/about/add', methods=['GET', 'POST'])
def add_about_section():
    if request.method == 'POST':
        section_key = request.form['section_key']
        title_ar = request.form.get('title_ar', '')
        title_en = request.form.get('title_en', '')
        content_ar = request.form.get('content_ar', '')
        content_en = request.form.get('content_en', '')
        image_url = request.form.get('image_url', '')
        order_index = request.form.get('order_index', 0)
        is_active = 1 if request.form.get('is_active') == 'on' else 0
        
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO about_sections 
                (section_key, title_ar, title_en, content_ar, content_en, image_url, order_index, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (section_key, title_ar, title_en, content_ar, content_en, image_url, order_index, is_active))
            conn.commit()
            conn.close()
            
            current_lang = get_language()
            if current_lang == 'ar':
                flash('تم إضافة القسم بنجاح!', 'success')
            else:
                flash('Section added successfully!', 'success')
            return redirect(url_for('dashboard_about'))
        except sqlite3.IntegrityError:
            conn.close()
            current_lang = get_language()
            if current_lang == 'ar':
                flash('هذا المفتاح موجود بالفعل!', 'error')
            else:
                flash('This section key already exists!', 'error')
    
    current_lang = get_language()
    return render_template('add_about_section.html', current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/about/edit/<int:section_id>', methods=['GET', 'POST'])
def edit_about_section(section_id):
    conn = get_db_connection()
    current_lang = get_language()
    
    if request.method == 'POST':
        title_ar = request.form.get('title_ar', '')
        title_en = request.form.get('title_en', '')
        content_ar = request.form.get('content_ar', '')
        content_en = request.form.get('content_en', '')
        image_url = request.form.get('image_url', '')
        order_index = request.form.get('order_index', 0)
        is_active = 1 if request.form.get('is_active') == 'on' else 0
        
        conn.execute('''
            UPDATE about_sections 
            SET title_ar = ?, title_en = ?, content_ar = ?, content_en = ?,
                image_url = ?, order_index = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title_ar, title_en, content_ar, content_en, image_url, order_index, is_active, section_id))
        conn.commit()
        conn.close()
        
        if current_lang == 'ar':
            flash('تم تحديث القسم بنجاح!', 'success')
        else:
            flash('Section updated successfully!', 'success')
        return redirect(url_for('dashboard_about'))
    
    section = conn.execute('SELECT * FROM about_sections WHERE id = ?', (section_id,)).fetchone()
    conn.close()
    
    if section is None:
        if current_lang == 'ar':
            flash('القسم غير موجود!', 'error')
        else:
            flash('Section not found!', 'error')
        return redirect(url_for('dashboard_about'))
    
    return render_template('edit_about_section.html', section=section, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/about/delete/<int:section_id>')
def delete_about_section(section_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM about_sections WHERE id = ?', (section_id,))
    conn.commit()
    conn.close()
    
    current_lang = get_language()
    if current_lang == 'ar':
        flash('تم حذف القسم بنجاح!', 'success')
    else:
        flash('Section deleted successfully!', 'success')
    return redirect(url_for('dashboard_about'))

# ============================================================================
# MESSAGES MANAGEMENT ROUTES
# ============================================================================

@app.route('/dashboard/messages')
def dashboard_messages():
    conn = get_db_connection()
    filter_type = request.args.get('filter', 'all')
    
    if filter_type == 'unread':
        messages = conn.execute('SELECT * FROM contact_messages WHERE is_read = 0 ORDER BY created_at DESC').fetchall()
    elif filter_type == 'read':
        messages = conn.execute('SELECT * FROM contact_messages WHERE is_read = 1 ORDER BY created_at DESC').fetchall()
    else:
        messages = conn.execute('SELECT * FROM contact_messages ORDER BY created_at DESC').fetchall()
    
    conn.close()
    current_lang = get_language()
    return render_template('dashboard_messages.html', messages=messages, filter_type=filter_type, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/messages/<int:message_id>')
def view_message(message_id):
    conn = get_db_connection()
    message = conn.execute('SELECT * FROM contact_messages WHERE id = ?', (message_id,)).fetchone()
    
    if message and not message['is_read']:
        conn.execute('UPDATE contact_messages SET is_read = 1 WHERE id = ?', (message_id,))
        conn.commit()
    
    conn.close()
    
    if message is None:
        current_lang = get_language()
        if current_lang == 'ar':
            flash('الرسالة غير موجودة!', 'error')
        else:
            flash('Message not found!', 'error')
        return redirect(url_for('dashboard_messages'))
    
    current_lang = get_language()
    return render_template('view_message.html', message=message, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

@app.route('/dashboard/messages/delete/<int:message_id>')
def delete_message(message_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM contact_messages WHERE id = ?', (message_id,))
    conn.commit()
    conn.close()
    
    current_lang = get_language()
    if current_lang == 'ar':
        flash('تم حذف الرسالة بنجاح!', 'success')
    else:
        flash('Message deleted successfully!', 'success')
    return redirect(url_for('dashboard_messages'))

# ============================================================================
# CONTACT INFO MANAGEMENT ROUTES
# ============================================================================

@app.route('/dashboard/contact-info', methods=['GET', 'POST'])
def dashboard_contact_info():
    conn = get_db_connection()
    
    if request.method == 'POST':
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        whatsapp = request.form.get('whatsapp', '')
        address_ar = request.form.get('address_ar', '')
        address_en = request.form.get('address_en', '')
        facebook = request.form.get('facebook', '')
        twitter = request.form.get('twitter', '')
        instagram = request.form.get('instagram', '')
        linkedin = request.form.get('linkedin', '')
        youtube = request.form.get('youtube', '')
        
        # Check if record exists
        existing = conn.execute('SELECT id FROM contact_info LIMIT 1').fetchone()
        
        if existing:
            conn.execute('''
                UPDATE contact_info 
                SET email = ?, phone = ?, whatsapp = ?, address_ar = ?, address_en = ?,
                    facebook = ?, twitter = ?, instagram = ?, linkedin = ?, youtube = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (email, phone, whatsapp, address_ar, address_en, facebook, twitter, instagram, linkedin, youtube, existing['id']))
        else:
            conn.execute('''
                INSERT INTO contact_info 
                (email, phone, whatsapp, address_ar, address_en, facebook, twitter, instagram, linkedin, youtube)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, phone, whatsapp, address_ar, address_en, facebook, twitter, instagram, linkedin, youtube))
        
        conn.commit()
        conn.close()
        
        current_lang = get_language()
        if current_lang == 'ar':
            flash('تم تحديث معلومات التواصل بنجاح!', 'success')
        else:
            flash('Contact info updated successfully!', 'success')
        return redirect(url_for('dashboard_contact_info'))
    
    contact_info = conn.execute('SELECT * FROM contact_info LIMIT 1').fetchone()
    conn.close()
    
    current_lang = get_language()
    return render_template('dashboard_contact_info.html', contact_info=contact_info, current_lang=current_lang, languages=SUPPORTED_LANGUAGES)

# API endpoint to handle contact form submission
@app.route('/api/contact', methods=['POST'])
def submit_contact():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone', '')
        governorate = data.get('governorate', '')
        message = data.get('message')
        
        # Save to database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO contact_messages (name, email, phone, governorate, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, phone, governorate, message))
        conn.commit()
        conn.close()
        
        current_lang = get_language()
        if current_lang == 'ar':
            success_message = 'شكراً لتواصلك معنا! سنرد عليك في أقرب وقت ممكن.'
        else:
            success_message = 'Thank you for contacting us! We will get back to you soon.'
        
        return jsonify({
            'success': True,
            'message': success_message
        }), 200
    except Exception as e:
        current_lang = get_language()
        if current_lang == 'ar':
            error_message = 'حدث خطأ. يرجى المحاولة مرة أخرى لاحقاً.'
        else:
            error_message = 'An error occurred. Please try again later.'
        
        return jsonify({
            'success': False,
            'message': error_message
        }), 500

# Error handler for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

# Error handler for 500
@app.errorhandler(500)
def internal_error(e):
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

