# Restaurant Management System

A full-stack restaurant management system separating the backend (Django), an admin dashboard (React/Vite), and a customer-facing portal (React/Vite).

## 🚀 Deployment & GitHub Guide

هذا الدليل خطوة بخطوة لشرح كيفية رفع الكود الخاص بك على GitHub ومن ثم نشره (Deploy) على منصات مجانية مثل Render (للباك-إند) و Vercel (للفرونت-إند وموقع العملاء).

---

### أولاً: الرفع على GitHub (خطوة بخطوة)

قم بفتح الـ **Terminal** داخل مجلد المشروع الرئيسي (Restaurant Management System) ونفذ الأوامر التالية بالترتيب:

#### 1. تهيئة المستودع (Initialize Repository)
```bash
git init
```

#### 2. إضافة الملفات للمستودع
بفضل ملفات الـ `.gitignore` التي قمنا بإنشائها، لن يتم رفع الملفات غير الضرورية (مثل `node_modules` و `.env`).
```bash
git add .
```

#### 3. حفظ التغييرات (Commit)
```bash
git commit -m "النسخة الأولى للمشروع جاهزة للإنتاج"
```

#### 4. إنشاء مستودع على موقع GitHub
1. اذهب إلى موقع [GitHub](https://github.com/) وسجل الدخول.
2. اضغط على زر **"+"** في الزاوية العلوية اليمنى واختر **"New repository"**.
3. اكتب اسم المستودع.
4. اجعله **Private** أو **Public** حسب رغبتك.
5. لا تقم بإضافة `README` أو `.gitignore` من الموقع.
6. اضغط **Create repository**.

#### 5. ربط المشروع المحلي بمستودع GitHub
بعد إنشاء المستودع سيعطيك GitHub أوامر مثل هذه لربط المستودع محليًا بـ GitHub. انسخها والصقها في الـ Terminal:
```bash
git branch -M main
git remote add origin https://github.com/اسم_حسابك/اسم_المستودع.git
git push -u origin main
```

---

### ثانياً: النشر (Deployment) خطوة بخطوة

سنقوم برفع **الباك-إند (Django)** على **Render** والأجزاء الأمامية **(React)** على **Vercel**.

#### 1- رفع الباك-إند على منحة Render مجاناً
1. افتح موقع [Render.com](https://render.com/) وسجل الدخول باستخدام حساب GitHub الخاص بك.
2. اضغط على **"New +"** واختر **"Web Service"**.
3. اربط حساب GitHub واختر المستودع.
4. **في إعدادات الـ Web Service:**
   - **Name:** `restaurant-backend`
   - **Root Directory:** اكتب `backend`
   - **Environment:** اختر `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command:**
     ```bash
     daphne -b 0.0.0.0 -p $PORT core.asgi:application
     ```
5. في **Environment Variables** للقيام بإضافة المتغيرات المطلوبة:
   - `SECRET_KEY`: اختر أي نص معقد سري.
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*` (مؤقتاً).
   - `PYTHON_VERSION`: `3.10.0`
6. سيقوم بالبناء ويعطيك رابط، مثلاً `https://restaurant-backend-xyz.onrender.com`.

---

#### 2- رفع لوحة الإدارة (Frontend) و موقع العملاء (Customer Website) على Vercel
قم بتنفيذ هذه الخطوات مرتين للفرونت إند وموقع العميل:
1. افتح موقع [Vercel.com](https://vercel.com/) وسجل الدخول بواسطة GitHub.
2. اضغط على **"Add New..."** ثم **"Project"**.
3. استورد المستودع.
4. **في إعدادات المشروع (Configure Project):**
   - **Framework Preset:** `Vite`
   - **Root Directory:** اختر ديركتوري سواء `frontend` أو `customer-website`.
5. في **Environment Variables**:
   - أضف `VITE_API_URL` وقم بوضع رابط الباك اند الذي حصلت عليه من Render كقيمة لهذا الحقل.
6. اضغط **Deploy**.

---

### 🚨 بعد النشر
لزيادة الحماية، اذهب إلى Render الخاص بالباك إند واستبدل قيمة `ALLOWED_HOSTS` المعمولة بشكل `*` لتكون روابط Vercel.

مثال:
- `ALLOWED_HOSTS` = `restaurant-backend.onrender.com,restaurant-admin.vercel.app`
- `CORS_ALLOWED_ORIGINS` = `https://restaurant-admin.vercel.app,https://restaurant-customer.vercel.app`

مبروك! مشروعك الآن يعمل بالكامل! 🚀
