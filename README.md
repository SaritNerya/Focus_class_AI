<div align="center">

# 🎯 FocusClass
### AI-Powered Real-Time Attention Analytics for Remote Learning

מערכת **Computer Vision** מבוססת בינה מלאכותית שמנתחת בזמן אמת את רמת הריכוז של תלמידות בשיעור מרוחק דרך המצלמה, ומזרימה תובנות חיות לדשבורד המרצה — בארכיטקטורת **Client-Server** מלאה, מאובטחת ברמה production-grade, ובנויה לפי עקרונות SOLID ותבניות עיצוב קלאסיות.

[![Python](https://img.shields.io/badge/Python-3.8%20--%203.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Google%20AI-4285F4?logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)
[![Architecture](https://img.shields.io/badge/Architecture-SOLID%20%2B%20Design%20Patterns-informational)]()

</div>

---

## 💡 מה זה עושה, בקצרה

תלמידה יושבת מול המצלמה שלה בשיעור מקוון. אלגוריתם **Computer Vision** מבוסס למידת מכונה קורא את הפנים שלה **בזמן אמת** — 478 נקודות ציון תלת-ממדיות על הפנים, 30 פעמים בשנייה — ומחלץ מהן ארבעה אינדיקטורים עצמאיים להיסח דעת: **עיניים עצומות, פיהוק, הטיית ראש, ותזוזת גוף מוגזמת**. מנוע ניקוד מבוסס-חוקים ממזג את הסיגנלים האלה לציון ריכוז חי בין 0-100, שולח אותו מאובטח לשרת, והמרצה רואה דשבורד בזמן אמת של כל הכיתה — מי ממוקדת ומי צריכה תשומת לב.

זה לא demo. זו מערכת שבנויה, מאובטחת, ונבדקת כמו שמערכת production אמיתית צריכה להיבנות.

---

## 🧠 בינה מלאכותית וראיית מכונה — הליבה הטכנולוגית

### מודל ה-ML הבסיסי: MediaPipe Face Landmarker
המערכת מבוססת על **MediaPipe** של Google — רשת נוירונים קונבולוציונית (CNN) מאומנת מראש, שמריצה **face detection + 3D landmark regression** בזמן אמת על CPU רגיל, ללא GPU. כל פריים וידאו מוזן למודל ומוחזרות 478 נקודות ציון תלת-ממדיות על פני הפנים (עיניים, פה, קווי מתאר, אף) — התשתית עליה בנוי כל שאר הפייפליין.

### אלגוריתמים גיאומטריים שבנינו מעל המודל
מהנקודות הגולמיות, המערכת מחלצת מדדים מספריים משמעותיים באמצעות אלגוריתמים קלאסיים בתחום ה-Computer Vision:

| אלגוריתם | מה הוא עושה | טכניקה |
|---|---|---|
| **EAR** (Eye Aspect Ratio) | זיהוי עצימת עיניים / מצמוץ | יחס גיאומטרי בין מרחקים אנכיים/אופקיים בין 6 נקודות ציון סביב העין (Soukupová & Čech) |
| **MAR** (Mouth Aspect Ratio) | זיהוי פיהוקים | אותה טכניקה, מותאמת לגיאומטריית הפה |
| **Head Pose Estimation** | חישוב זווית pitch/yaw/roll של הראש | **PnP (Perspective-n-Point)** באמצעות `cv2.solvePnP` — התאמת מודל פנים גנרי תלת-ממדי לנקודות דו-ממדיות, פירוק מטריצת סיבוב (Rodrigues + `RQDecomp3x3`) לזוויות אוילר |
| **Motion Tracking** | זיהוי חוסר שקט (fidgeting) | מעקב מרחק אוקלידי של נקודת האף בין פריימים עוקבים |

### כיול אישי אדפטיבי (Adaptive Personal Calibration)
במקום ספים קבועים מראש (hardcoded thresholds) שלא מתאימים לכל בנאדם, המערכת אוספת מדגם התנהגות אישי ב-3 השניות הראשונות ומחשבת **סף EAR דינמי סטטיסטי**: `ממוצע − 2·סטיית תקן`, בדומה לגישת z-score — כך שהמערכת מתכיילת אוטומטית לצורת עיניים שונה מאדם לאדם.

### סינון סיגנל וייצוב (Signal Processing)
זוויות הראש הגולמיות מה-PnP רועשות מטבען. המערכת מיישמת **EMA — Exponential Moving Average** (`α·x_t + (1-α)·x_{t-1}`) על זוויות ה-yaw/roll לפני שהן נכנסות למנוע הניקוד, כדי לנטרל רעש high-frequency בלי לפגוע בזמן תגובה.

### מיזוג רב-סיגנלי ומנוע החלטה (Multi-Signal Decision Fusion)
ארבעת הסיגנלים העצמאיים (תזוזה, עיניים, הטיה, פיהוק) ממוזגים ל**ציון ריכוז אחוד** דרך שרשרת **Decorator** (ראו פירוט ארכיטקטוני למטה) — כל אחד תורם "תקרת ציון" עצמאית, והמערכת בוחרת תמיד את המגבלה המחמירה ביותר. מעל זה בנוי **state machine להתאוששות הדרגתית**: ירידה בציון תמיד מיידית (0 סבלנות להיסח דעת), אך עלייה חזרה למעלה הדרגתית, עם מצב "התאוששות איטית" חכם לאחר אירוע ממושך במיוחד (עוגן לממוצע נגלל של הדקה האחרונה) — מונע "קפיצות" לא-ריאליסטיות בציון ומדמה תשומת לב אנושית אמיתית.

---

## 🏗️ ארכיטקטורה ותבניות עיצוב (Design Patterns)

הפרויקט בנוי כשני שירותים עצמאיים לחלוטין (Client + Server) המתקשרים אך ורק דרך HTTP מאובטח, כל אחד עם שכבות אחריות ברורות (Vision → Calibration → Scoring → Networking בלקוח; API → Security → Domain → Services → Repositories → DB בשרת) התואמות לעקרונות **SOLID**.

| תבנית | שימוש בפועל | הבעיה שהיא פותרת |
|---|---|---|
| 🎁 **Decorator** | שרשרת ניקוד ההיסח דעת (`FocusEvaluator` chain) | הוספת סוג היסח-דעת חדש = מחלקה אחת חדשה, **אפס** שינוי בקוד קיים (Open/Closed Principle) |
| 🎁 **Decorator** (שוב, בשרת) | `PersistingStudentRepository` עוטף `InMemoryRepository` | מוסיף שמירה מתמשכת ל-DB מעל cache מהיר, ללא שינוי בצרכנים קיימים |
| 🔌 **Strategy + Null Object** | בחירת מצלמה וירטואלית (`VirtualCamera`) בזמן ריצה | קוד קורא אחיד, בלי `if driver_exists` מפוזר בכל מקום |
| 🗄️ **Repository** | שכבת גישה לנתונים בשרת | מפרידה לוגיקה עסקית מהמימוש הפיזי (זיכרון / SQLite) |
| 🏭 **Factory** | `create_app()`, `evaluator_factory` | הרכבה מבוקרת של גרפי אובייקטים מורכבים במקום מרכזי אחד |
| 🎭 **Facade** | `FaceFeatureExtractor` | מסתיר מורכבות של 4 אלגוריתמים גיאומטריים מאחורי `extract()` אחד |
| 💉 **Dependency Injection** | לאורך כל השרת (FastAPI `Depends`) + `ScoringConfig` | הפרדת קונפיגורציה מלוגיקה — טסטבילי, ניתן להחלפה |

---

## 🔒 אבטחת מידע (Production-Grade Security)

לא "פרויקט לימודי עם הערת TODO על אבטחה" — כל שכבה מוגנת בפועל:

- 🔑 **אימות API מבוסס Bearer Token** בין הלקוח לשרת, מושווה עם `secrets.compare_digest` (חסין Timing Attack)
- 🔐 **סיסמת דשבורד מוצפנת** — `bcrypt` בלבד, **אפס** סיסמאות בטקסט גלוי בקוד או בקבצי קונפיגורציה
- 🛡️ **ולידציית קלט קפדנית בגבול הרשת** — Pydantic v2 schemas עם allowlist regex, הגבלות אורך, ניקוי תווי בקרה — הגנה מפני XSS/הזרקות **לפני** שקלט נוגע בלוגיקה עסקית
- 🗃️ **הגנה מובנית מ-SQL Injection** — 100% SQLAlchemy ORM, אפס SQL גולמי המחובר לקלט משתמש
- ⏱️ **Rate Limiting** — sliding window פר-IP למניעת הצפה/brute-force
- 🧱 **Security Headers** — `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` בכל תגובה
- 🌐 **CORS מוגבל כברירת מחדל** — חסימת בקשות ממקורות לא מוכרים
- 🙈 **Zero secrets in code** — הכל דרך משתני סביבה (`.env`), מודל 12-factor app
- 🚫 **Error handling ללא דליפת מידע** — שגיאות ללקוח גנריות, פירוט מלא רק ב-log השרת

---

## 🧰 מחסנית טכנולוגית

<table>
<tr><td><b>Computer Vision / ML</b></td><td>MediaPipe (Google), OpenCV, NumPy</td></tr>
<tr><td><b>Backend</b></td><td>FastAPI, Uvicorn (ASGI), Pydantic v2, SQLAlchemy 2.0, SQLite</td></tr>
<tr><td><b>Security</b></td><td>Passlib + bcrypt, Bearer-token auth, custom rate limiting middleware</td></tr>
<tr><td><b>Client</b></td><td>Python, OpenCV GUI, Requests, threading (async score submission)</td></tr>
<tr><td><b>Testing</b></td><td>pytest, FastAPI TestClient (httpx) — unit + integration tests</td></tr>
<tr><td><b>DevOps</b></td><td>python-dotenv, venv isolation, Inno Setup (Windows installer packaging)</td></tr>
<tr><td><b>Architecture</b></td><td>SOLID, 7 Design Patterns, Clean Architecture, layered separation</td></tr>
</table>

---

## 📐 תרשימי ארכיטקטורה (UML)

הפרויקט כולל תיעוד UML מלא ומדויק (7 תרשימים: ארכיטקטורת מערכת, Class Diagrams, Sequence Diagram) שנבנה ונבדק ברינדור אמיתי — ראו [`UML.html`](UML.html).

לתיעוד הטכני המלא (כולל כל החלטה ארכיטקטונית, באגים שתוקנו מהקוד המקורי, והוראות התקנה מפורטות) ראו [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## 🎯 מה הפרויקט הזה מדגים

- ✅ **אינטגרציה מלאה עם מודל ML** בפרודקשן — לא רק "קריאה ל-API", אלא בניית pipeline שלם סביבו: feature engineering, כיול אדפטיבי, סינון סיגנל, ומיזוג החלטות
- ✅ **ארכיטקטורת Full-Stack אמיתית** — הפרדת client/server מלאה, שכבות אחריות ברורות, תקשורת HTTP מאובטחת
- ✅ **חשיבה אבטחתית מובנית (Security by Design)** — לא תוספת בדיעבד
- ✅ **קוד נבדק (Tested)** — unit tests לאלגוריתמי הניקוד, integration tests ל-API עם TestClient אמיתי
- ✅ **משמעת הנדסית** — כל תיקון/פיצ'ול נבדק בפועל בסביבות ריצה אמיתיות (כולל תאימות חוצת-גרסאות Python 3.8–3.11), לא רק "נראה תקין"
- ✅ **ידע בתבניות עיצוב קלאסיות** ויישום מעשי שלהן לבעיה אמיתית, לא תרגיל אקדמי

---

## ⚙️ הרצה מהירה

```bash
# שרת
cd server && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m server.main

# לקוח (טרמינל נפרד)
cd client && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install --no-deps -r requirements-mediapipe.txt
python -m client.main
```

הוראות מלאות, כולל Windows ו-troubleshooting: [`ARCHITECTURE.md`](ARCHITECTURE.md#התקנה-והרצה)

---

<div align="center">

**נבנה עם דגש על ארכיטקטורה נכונה, אבטחה אמיתית, ושימוש מושכל בכלי AI/ML מודרניים.**

</div>
