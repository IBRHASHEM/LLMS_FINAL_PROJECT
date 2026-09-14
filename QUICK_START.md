# ⚡ Quick Start Guide
## البدء السريع - 5 دقائق

---

## 🎯 الهدف
تشغيل المشروع في أقل من 5 دقائق

---

## ⏱️ الخطوات (5 دقائق)

### دقيقة 1️⃣ : التثبيت الأساسي

```bash
# 1. انسخ المجلد المشروع

# 2. افتح Terminal/Command Prompt

# 3. اذهب إلى المجلد
cd path/to/project

# 4. أنشئ virtual environment
python -m venv venv

# 5. فعله
# على Windows:
venv\Scripts\activate

# على Mac/Linux:
source venv/bin/activate
```

### دقيقة 2️⃣ : تثبيت المكتبات

```bash
# أحتاج الإنترنت (5 MB)
pip install -r requirements.txt
```

### دقيقة 3️⃣ : تكوين API Keys

```bash
# 1. انسخ ملف البيئة
cp .env.example .env

# 2. حصل على API Keys (مجاني):
#    - Groq: https://console.groq.com
#    - Google: https://makersuite.google.com/app/apikey

# 3. فتح .env وأضف المفاتيح:
# GROQ_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here
```

### دقيقة 4️⃣ : التشغيل

```bash
# الطريقة الأولى - Web Interface (سهل):
python run.py
# اختر option 1

# أو مباشرة:
streamlit run app.py
```

### دقيقة 5️⃣ : استخدم!

```
المتصفح سيفتح تلقائياً على:
👉 http://localhost:8501
```

---

## 🎯 الآن يمكنك:

### 1. البحث (Research Tab)
```
1. اكتب سؤالك: "What are LLMs?"
2. اضغط "Start Research"
3. استنتظر النتيجة (30-60 ثانية)
4. شوف التقرير!
```

### 2. المحادثة (Chat Tab)
```
1. اكتب: "Tell me more about transformers"
2. اضغط Send
3. NeuroBot يرد فوراً!
```

### 3. الذاكرة (Memory Tab)
```
1. شوف ما تم حفظه
2. ابحث في السابق
3. إعادة استخدام البحث
```

---

## 🐛 مشاكل شائعة وحلول

### ❌ "ModuleNotFoundError"
```bash
الحل:
pip install -r requirements.txt
```

### ❌ "API Key Invalid"
```
الحل:
1. تأكد من .env موجود
2. تأكد من المفاتيح صحيحة
3. تأكد من الإنترنت متصل
```

### ❌ "port 8501 already in use"
```bash
الحل:
streamlit run app.py --server.port 8502
```

### ❌ "Slow responses"
```
الحل:
1. اضغط استناري قليل أكثر
2. تأكد من الإنترنت سريع
3. استخدم model أسرع في .env
```

---

## 📚 الملفات المهمة

```
├── app.py              👈 الواجهة الرسمية (ابدأ هنا!)
├── orchestrator.py     👈 الدماغ الرئيسي
├── config_agents.py    👈 إعداد الأجنحة
├── neurobot_chat.py    👈 المحادثة الذكية
└── requirements.txt    👈 المكتبات المطلوبة
```

---

## 🚀 الأوامر السريعة

```bash
# تشغيل التطبيق
python run.py

# أو مباشرة
streamlit run app.py

# اختبار سريع
python -c "from config_agents import *; print('✅ OK')"

# حذف الذاكرة (ابدأ جديد)
rm -rf memory_db

# تحديث المكتبات
pip install -r requirements.txt --upgrade
```

---

## 💡 نصائح سريعة

```
✅ للنتائج الأفضل:
   - سؤال واضح وصريح
   - كلمات مفتاحية محددة
   - صبر على الاستجابة

✅ للبحث الأسرع:
   - أسئلة قصيرة
   - مواضيع محددة
   - تجنب الأسئلة المعقدة جداً

✅ للمحادثة الأفضل:
   - ابدأ بسياق واضح
   - اسأل أسئلة متابعة
   - استخدم "أخبرني أكثر"
```

---

## 📞 هل تحتاج مساعدة؟

```
❓ الأسئلة الشائعة:

Q: كم التكاليف؟
A: مجاني! (إذا استخدمت free tiers)

Q: هل يحتاج انترنت؟
A: نعم، للبحث والنماذج

Q: هل يحفظ البيانات؟
A: نعم، في memory_db/ محلياً

Q: هل آمن؟
A: نعم، كل شيء محلي بدون سرقة بيانات
```

---

## ✅ Checklist للتحقق

```
☑️ Python 3.9+ مثبت؟
   python --version

☑️ Virtual environment فعال؟
   (يجب ترى (venv) قبل الـ command)

☑️ المكتبات مثبتة؟
   pip list | grep streamlit

☑️ API Keys موجودة؟
   cat .env (على Mac/Linux)
   type .env (على Windows)

☑️ الإنترنت متصل؟
   ping google.com

☑️ التطبيق يشتغل؟
   streamlit run app.py
```

---

## 🎓 الخطوة التالية

بعد التشغيل الناجح:

1. **جرب البحث**
   - جرب موضوع تهتم به
   - اتفرج على التقرير النهائي

2. **تحادث مع NeuroBot**
   - اسأل أسئلة متابعة
   - شوف كيف يتذكر السياق

3. **استكشف الذاكرة**
   - ابحث عن أبحاث سابقة
   - جرب Semantic Search

4. **اقرأ التوثيق الكامل**
   - README.md للتفاصيل
   - PRESENTATION_GUIDE.md للشرح

---

## 🎉 ماتوانسة!

الآن أنت جاهز تستخدم النظام!

```
تدفق الاستخدام:

   البحث
     ↓
  التحليل
     ↓
  التقرير
     ↓
  المحادثة
     ↓
  الحفظ في الذاكرة
```

---

**استمتع بالمشروع! 🚀**

أي أسئلة؟ اقرأ README.md أو PRESENTATION_GUIDE.md

---

*آخر تحديث: 2024*
