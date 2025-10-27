# تحديث نموذج الاتصال - Contact Form Update

## التغييرات / Changes

### العربية
تم تحديث نموذج الاتصال ليشمل الحقول التالية:
1. **الاسم الكامل** (Full Name) - مطلوب
2. **البريد الإلكتروني** (Email) - مطلوب
3. **رقم الهاتف** (Phone Number) - مطلوب
4. **المحافظة** (Governorate) - مطلوب
5. **ملاحظات** (Notes) - مطلوب

تم إزالة الحقول التالية:
- ~~اسم الشركة~~ (Company Name)
- ~~نوع الفيزا~~ (Visa Type)

---

### English
The contact form has been updated to include the following fields:
1. **Full Name** - Required
2. **Email Address** - Required
3. **Phone Number** - Required
4. **Governorate / State** - Required
5. **Notes** - Required

The following fields have been removed:
- ~~Company Name~~
- ~~Visa Type~~

---

## الملفات المعدلة / Modified Files

### 1. Backend (Python)
- **`app.py`**
  - Updated database schema for `contact_messages` table
  - Added `phone` and `governorate` columns
  - Updated API endpoint `/api/contact` to handle new fields
  - Added Arabic and English translations for new labels

### 2. Frontend (HTML/CSS)
- **`templates/index.html`**
  - Updated contact form with new input fields
  - Added phone number field (type: tel)
  - Added governorate field (type: text)
  - Removed company and visa type fields
  - Updated all labels with bilingual support

### 3. JavaScript
- **`static/tooplate-cloud-scripts.js`**
  - Updated form submission handler
  - Changed to use `fetch` API for real form submission
  - Updated form data structure to include phone and governorate

### 4. Dashboard Templates
- **`templates/view_message.html`**
  - Updated to display phone and governorate instead of company and visa type
  - Added appropriate icons for new fields

- **`templates/dashboard_messages.html`**
  - Updated message list to show phone and governorate
  - Updated message metadata display

---

## خطوات التثبيت / Installation Steps

### الطريقة الأولى: تشغيل السكريبت التلقائي
Run the automatic update script:

```bash
python update_contact_fields.py
```

هذا السكريبت سيقوم بـ:
This script will:
1. Add the `phone` column to `contact_messages` table
2. Add the `governorate` column to `contact_messages` table
3. Keep old columns for backward compatibility

### الطريقة الثانية: التحديث اليدوي
Manual database update:

```sql
-- Add new columns
ALTER TABLE contact_messages ADD COLUMN phone TEXT;
ALTER TABLE contact_messages ADD COLUMN governorate TEXT;

-- Optional: Remove old columns (if you don't need them)
-- ALTER TABLE contact_messages DROP COLUMN company;
-- ALTER TABLE contact_messages DROP COLUMN visa_type;
```

---

## الترجمات / Translations

تم إضافة الترجمات التالية في قاعدة البيانات:
The following translations have been added to the database:

| Key | English | Arabic |
|-----|---------|--------|
| phone_label | Phone Number | رقم الهاتف |
| phone_placeholder | +1 234 567 8900 | +20 123 456 7890 |
| governorate_label | Governorate / State | المحافظة |
| governorate_placeholder | Select your governorate | اختر محافظتك |
| notes_label | Notes | ملاحظات |

---

## اختبار النموذج / Testing the Form

1. افتح الموقع / Open the website: `http://localhost:5000`
2. انتقل إلى قسم "تواصل معنا" / Navigate to "Contact" section
3. املأ النموذج بالبيانات التالية / Fill the form with test data:
   - الاسم / Name: أحمد محمد / John Doe
   - البريد / Email: ahmed@example.com
   - الهاتف / Phone: +20 123 456 7890
   - المحافظة / Governorate: القاهرة / Cairo
   - الملاحظات / Notes: اختبار النموذج / Testing form
4. اضغط "إرسال" / Click "Submit"
5. تحقق من لوحة التحكم / Check Dashboard > Messages

---

## الملاحظات المهمة / Important Notes

### العربية
- جميع الحقول الجديدة مطلوبة (required)
- حقل الهاتف يستخدم نوع `tel` للتوافق مع الأجهزة المحمولة
- حقل المحافظة هو حقل نصي، يمكن تحويله لقائمة منسدلة لاحقاً
- الحقول القديمة (company, visa_type) تبقى في قاعدة البيانات للتوافق مع البيانات القديمة
- يمكن حذف الحقول القديمة يدوياً إذا لم تكن بحاجة لها

### English
- All new fields are required
- Phone field uses `tel` type for mobile device compatibility
- Governorate field is a text input, can be converted to dropdown later
- Old fields (company, visa_type) remain in database for backward compatibility
- You can manually delete old fields if not needed

---

## التحسينات المستقبلية / Future Improvements

### اقتراحات للتطوير / Suggested Enhancements

1. **قائمة منسدلة للمحافظات** / Governorate Dropdown
   - إضافة قائمة بالمحافظات المصرية أو الدول
   - Add list of Egyptian governorates or countries

2. **التحقق من رقم الهاتف** / Phone Validation
   - إضافة validation للتأكد من صحة رقم الهاتف
   - Add validation to ensure phone number is valid

3. **رمز الدولة التلقائي** / Auto Country Code
   - إضافة country code selector للهاتف
   - Add country code selector for phone numbers

4. **حفظ محافظة المستخدم** / Save User Location
   - حفظ الموقع تلقائياً باستخدام IP geolocation
   - Auto-save location using IP geolocation

---

## الدعم / Support

إذا واجهت أي مشكلة، تواصل معنا:
If you encounter any issues, contact us:

- Email: support@elegant.com
- Dashboard: http://localhost:5000/dashboard

---

**آخر تحديث / Last Updated:** October 21, 2025
**الإصدار / Version:** 2.0

