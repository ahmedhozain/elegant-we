# دليل نشر الموقع على Render

## خطوات النشر:

### 1. إنشاء حساب على Render
- اذهب إلى [Render.com](https://render.com)
- سجل حساب جديد أو سجل دخول

### 2. ربط المستودع
- اضغط على "New +" في لوحة التحكم
- اختر "Web Service"
- اربط حسابك على GitHub/GitLab
- اختر المستودع الخاص بالمشروع

### 3. إعدادات النشر
Render سيكتشف تلقائياً ملف `render.yaml` ويستخدم الإعدادات التالية:

**Build Command:**
```bash
./build.sh
```

**Start Command:**
```bash
gunicorn app:app
```

**Environment:**
- Python Version: 3.11.0
- SECRET_KEY: سيتم توليده تلقائياً

### 4. متغيرات البيئة (اختياري)
يمكنك إضافة متغيرات إضافية في لوحة التحكم:
- `SECRET_KEY` - سيتم توليده تلقائياً
- أي متغيرات أخرى تحتاجها

### 5. نشر الموقع
- اضغط على "Create Web Service"
- انتظر حتى يكتمل البناء والنشر
- سيتم إعطاؤك رابط للموقع مثل: `https://your-app-name.onrender.com`

## الملفات المهمة للنشر:

### ✅ الملفات الموجودة:
- `requirements.txt` - حزم Python المطلوبة
- `app.py` - تطبيق Flask الرئيسي
- `build.sh` - سكريبت البناء
- `render.yaml` - إعدادات Render
- `.gitignore` - الملفات المستبعدة من Git

### 📝 ملاحظات مهمة:

1. **قاعدة البيانات:**
   - قاعدة البيانات SQLite تعمل على Render لكنها ستُحذف عند إعادة النشر
   - للإنتاج، يُفضل استخدام PostgreSQL من Render

2. **الملفات المرفوعة:**
   - الصور والفيديوهات ستُحذف عند إعادة النشر
   - يُفضل استخدام خدمة تخزين سحابي مثل AWS S3 أو Cloudinary

3. **الأداء:**
   - النسخة المجانية من Render تنام بعد 15 دقيقة من عدم الاستخدام
   - أول طلب بعد النوم سيكون بطيئاً قليلاً

## ترقية لقاعدة بيانات دائمة (اختياري):

### استخدام PostgreSQL:
1. في Render، أنشئ "PostgreSQL Database"
2. احصل على رابط الاتصال (Connection String)
3. حدّث `app.py` لاستخدام PostgreSQL بدلاً من SQLite
4. أضف `psycopg2-binary` في `requirements.txt`

مثال:
```python
import os
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///website_content.db')
```

## الدعم والمساعدة:
- [توثيق Render](https://render.com/docs)
- [توثيق Flask](https://flask.palletsprojects.com/)

---
تم إنشاء هذا الدليل لمساعدتك في نشر موقع Elegant Immigration Services 🚀

