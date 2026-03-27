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

سنقوم برفع **الباك-إند (Django)** على **Railway** والأجزاء الأمامية **(React)** على **Vercel**.

#### 1- رفع الباك-إند مجاناً على Railway
1. افتح موقع [Railway.app](https://railway.app/) وسجل الدخول باستخدام حساب GitHub الخاص بك.
2. للبدء، ستظهر لك لوحة التحكم الرئيسية فاضغط على زر **"New Project"**.
3. اختر **"Deploy from GitHub repo"**.
4. اختر المستودع الخاص بك (مثل `Restaurant-system`).
5. **مهم جداً (Root Directory):** بمجرد أن يظهر المشروع في واجهة Railway، اضغط عليه، واذهب إلى الإعدادات (**Settings**)، ثم تحت قسم **Service**، ابحث عن الحقل المسمى **Root Directory** واكتب فيه `backend`، ثم اضغط علامة الصح أو `Save`. (هذا سيجعل Railway يفهم أن الباك-إند كله داخل هذا المجلد).
6. اذهب إلى قائمة **Variables** (المتغيرات) وأضفها بالضغط على `New Variable` أو `RAW Editor` للصقها جميعاً معاً:
   ```env
   SECRET_KEY=vHLPyWbAXJUJ8BivxboHA1zk251LWzQ1wyUxxMgwdCb3dg8ztJ_jNdRRkScAgST40OQ
   DEBUG=False
   ALLOWED_HOSTS=*
   CORS_ALLOWED_ORIGINS=https://localhost:5173
   SECURE_SSL_REDIRECT=True
   PYTHON_VERSION=3.10.0
   ```
7. ستقوم المنصة تلقائيًا بالبناء والتشغيل بناءً على ملف `Procfile` الذي جهزناه.
8. اذهب إلى قائمة **Settings** ثم انزل لتجد **Networking**، تحت كلمة **Public Networking** اضغط على **Generate Domain** ليصنع لك رابطاً عاماً لمشروعك (مثلاً: `restaurant-system.up.railway.app`). هذا الرابط هو ما سنستخدمه!

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
   - أضف المتغير `VITE_API_URL` وضع فيه قيمة الرابط الخاص بالباك اند من Railway (مثلاً: `https://restaurant-system.up.railway.app`).
6. اضغط **Deploy**.

---

### 🚨 بعد النشر
لزيادة الحماية، اذهب إلى Railway مجدداً وعدّل قيمة `ALLOWED_HOSTS` المعمولة بشكل `*` لتكون روابط موقع Vercel فقط.

مثال:
- `ALLOWED_HOSTS` = `restaurant-system.up.railway.app,restaurant-admin.vercel.app`
- `CORS_ALLOWED_ORIGINS` = `https://restaurant-admin.vercel.app,https://restaurant-customer.vercel.app`

مبروك! مشروعك الآن يعمل بالكامل! 🚀
