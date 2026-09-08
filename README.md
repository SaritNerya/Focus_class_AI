# FocusClass

מערכת לניטור רמת ריכוז תלמידות בשיעור מרחוק, בעזרת ניתוח פנים בוידאו (עצימת
עיניים, פיהוקים, הטיית ראש, תזוזה) ודשבורד חי למרצה.

הפרויקט מחולק לשני חלקים עצמאיים לחלוטין, שמתקשרים רק דרך HTTP:

```
Focus_class/
├── client/     # רץ אצל כל תלמידה - Python + OpenCV + MediaPipe
├── server/     # שרת המרצה - FastAPI, יכול לרוץ על מחשב אחד לכל הכיתה
├── dependencies/   # דרייברים למצלמה וירטואלית (Unity Capture)
└── setup_installer.iss   # סקריפט Inno Setup לאריזת הלקוח כ-.exe
```

## למה מבנה כזה?

- **הפרדה מלאה בין לקוח לשרת** - כל צד יש לו `requirements.txt`, `.env`
  וקוד עצמאיים. הלקוח לא תלוי ב-FastAPI, השרת לא תלוי ב-OpenCV.
- **שכבות ברורות בכל צד** (vision / scoring / networking / ui בלקוח;
  api / services / repositories / db בשרת) - כל שכבה אחראית על דבר אחד
  (Single Responsibility), ותלויה בממשקים מופשטים ולא במימושים קונקרטיים
  (Dependency Inversion).

## תבניות עיצוב עיקריות

| תבנית | איפה | למה |
|---|---|---|
| **Decorator** | `client/scoring/decorators/*` | כל "עונש" (תזוזה, עיניים עצומות, הטיה, פיהוק) הוא שכבה שעוטפת את הקודמת. הוספת עונש חדש = מחלקה חדשה + שורה אחת ב-factory, בלי לגעת בקוד קיים. |
| **Decorator (שוב)** | `server/repositories/persisting_repository.py` | עוטפת את ה-cache בזיכרון בהתנהגות שמירה ל-DB, מבלי לשנות אף קוד אחר שמשתמש ב-repository. |
| **Strategy + Null Object** | `client/core/virtual_camera.py` | בוחר backend מתאים (Unity/OBS) בזמן ריצה; אם אין אף אחד - `NullVirtualCamera` מבטלת את הצורך ב-`if has_vcam` בכל מקום. |
| **Repository** | `server/repositories/` | מפרידה לוגיקה עסקית מהשאלה "איפה שמור המידע" (זיכרון + SQLite). |
| **Factory** | `server/app.py: create_app()`, `client/scoring/evaluator_factory.py` | הרכבת אובייקטים מורכבים במקום אחד ומבודד. |
| **Facade** | `client/vision/feature_extractor.py` | מסתיר את כל חישובי ה-EAR/MAR/pose האינדיבידואליים מאחורי ממשק `extract()` אחד. |
| **Dependency Injection** | כל השרת (FastAPI `Depends`), `ScoringConfig` בלקוח | ספים, repositories ו-services מוזרקים ולא hardcoded - קל לבדוק ולהחליף. |

## אבטחת מידע

1. **אימות בין הלקוח לשרת** - כל בקשת POST חייבת לשאת `Authorization: Bearer <API_KEY>`
   זהה למפתח שמוגדר בשרת (`server/core/security.py::require_api_key`),
   מושווה בעזרת `secrets.compare_digest` (חסין Timing Attack).
2. **הגנת הדשבורד** - HTTP Basic Auth; הסיסמה **לעולם לא נשמרת בטקסט גלוי**,
   רק כ-bcrypt hash (`server/scripts/generate_password_hash.py`).
3. **ולידציה קפדנית בגבול הרשת** - כל קלט עובר Pydantic schema
   (`server/domain/schemas.py`): allowlist תווים, הגבלות אורך, ניקוי תווי
   בקרה - מונע הזרקות (למשל HTML/Script) עוד לפני שהנתון נוגע בלוגיקה
   העסקית. הלקוח מבצע סניטציה דומה כשכבת הגנה נוספת (Defense in Depth).
4. **מניעת SQL Injection** - כל גישה ל-DB דרך SQLAlchemy ORM (parameterized
   queries), אין שום SQL גולמי מחובר לקלט משתמש.
5. **Rate limiting** - הגבלת קצב בקשות פר-IP (`server/core/rate_limit.py`)
   מגינה מפני הצפה/ניחוש brute-force.
6. **Security headers** - `X-Frame-Options`, `X-Content-Type-Options`,
   `Referrer-Policy` בכל תגובה (`server/core/security_headers.py`).
7. **CORS מוגבל** - ברירת המחדל חוסמת בקשות דפדפן ממקורות לא מוכרים; יש
   להגדיר `CORS_ORIGINS` בפירוש אם צריך.
8. **אין סודות בקוד** - `API_KEY`, סיסמאות והגדרות רגישות נטענים אך ורק
   מ-`.env` (ראו `.env.example` בכל תיקייה), שלא נכנס ל-git (`.gitignore`).
9. **הודעות שגיאה לא חושפות פרטים פנימיים** - שגיאות בלתי צפויות מוחזרות
   כהודעה גנרית ללקוח, בעוד הפירוט המלא נרשם רק ב-log של השרת.

## תיקוני באגים/ליקויים שנמצאו בקוד המקורי

- **`DataLogger` היה חסר לגמרי** - `main.py` המקורי ייבא מודול שלא קיים
  בפרויקט (`focus_logic.data_logger`), מה שהיה שובר את ההרצה. מומש מחדש
  ב-`client/session_logging/data_logger.py`.
- **כיול כפול וסותר** - הקוד המקורי כייל בסיס אישי פעמיים במקומות שונים
  (`main.py` לפי מספר פריימים, `scoring.py` לפי זמן) בלי שהם מסונכרנים.
  אוחד למקור אמת יחיד ב-`client/core/calibration.py`.
- **אין הגנה על נתיבי השרת** - כל אחד יכל לשלוח ציונים מזויפים או לצפות
  בדשבורד. נפתר עם API key + Basic Auth (ראו מעלה).
- **אין שמירה קבועה של נתונים** - נתוני התלמידות היו רק ב-dict בזיכרון
  ונעלמו בכל הפעלה מחדש. נוסף SQLite לצורך היסטוריה/ביקורת.

## התקנה והרצה

### שרת (מחשב המרצה)

```bash
cd server
python -m venv .venv && source .venv/bin/activate   # ב-Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
python -m server.scripts.generate_password_hash     # מייצר DASHBOARD_PASSWORD_HASH
# ערכו את .env: הדביקו את ה-hash, הגדירו API_KEY אקראי וארוך, DASHBOARD_USERNAME

cd ..
python -m server.main
```

השרת יאזין על `http://<כתובת-המחשב>:8000`. הדשבורד זמין ב-`/` (מבקש שם
משתמש+סיסמה בדפדפן).

### לקוח (מחשב כל תלמידה)

```bash
cd client
python -m venv .venv && source .venv/bin/activate   # ב-Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install --no-deps -r requirements-mediapipe.txt

cp .env.example .env
# ערכו את .env: SERVER_URL לכתובת השרת, API_KEY זהה בדיוק לזה שבשרת

cd ..
python -m client.main
```

> **חשוב: Python חייב להיות גרסת 64-ביט.** מדיהפייפ (הספרייה שמזהה את
> הפנים) מעולם לא פרסמה גרסת 32-ביט ל-Windows בשום גרסה שלה - התקנה על
> Python 32-ביט תיכשל תמיד, בלי קשר לגרסה שנבחר. בדקי מראש:
> ```powershell
> python -c "import struct; print(struct.calcsize('P') * 8)"
> ```
> אם זה מדפיס `32` - יש להתקין Python 64-ביט (מומלץ: Python 3.11, מ-
> python.org, לוודא שבוחרים ב-"Windows installer (64-bit)").
>
> **למה שני קבצי requirements ולמה `--no-deps`?**
> מדיהפייפ מכריז ב-metadata שלו על תלות חובה בחבילות כבדות ולא רלוונטיות
> (`jax`, `jaxlib`, `torch`, `sounddevice`, `opencv-contrib-python`) גם למי
> שמשתמש רק ב-FaceMesh כמונו - ועל Python 3.8 בפרט, ל-`jaxlib` אין בכלל
> wheel זמין ב-PyPI, כך ש-`pip install mediapipe` רגיל נכשל לגמרי. הפתרון:
> מתקינים קודם את `requirements.txt` (כולל התלויות **האמיתיות** של
> מדיהפייפ בזמן ריצה - matplotlib, absl-py, attrs, flatbuffers, protobuf),
> ואז את מדיהפייפ עצמו עם `--no-deps` כדי לדלג על התלויות המיותרות.
>
> `requirements-mediapipe.txt` בוחר אוטומטית גרסת מדיהפייפ מתאימה לפי גרסת
> ה-Python שלכם (Python 3.8 לעומת 3.9+), ומגביל אותה ל-`<0.10.22` - **גם
> על Python חדש** - כי אימתנו בפועל שהחל מגרסה `0.10.30` מדיהפייפ הסירה
> לגמרי את ה-API הישן (`mp.solutions`) שעליו כל קוד הזיהוי כאן מבוסס.
>
> נבדק בפועל, מקצה לקצה, גם על Python 3.8 וגם על Python 3.11: FaceMesh,
> `process()` ו-`drawing_utils` עובדים תקין בשני המקרים.

## הרצת בדיקות

```bash
pip install pytest httpx
pytest tests/server   # לא דורש cv2/mediapipe
pytest tests/client    # דורש את requirements.txt של הלקוח מותקן
```

## מבנה מפורט

```
client/
├── main.py                 # נקודת כניסה דקה
├── app.py                  # FocusSessionApp - composition root, לולאת הווידאו
├── config.py                # הגדרות מ-.env
├── core/
│   ├── camera_capture.py    # ניהול מצלמה פיזית
│   ├── virtual_camera.py    # Strategy + Null Object למצלמה וירטואלית
│   ├── calibration.py       # כיול אישי מאוחד
│   └── validators.py        # סניטציית קלט
├── vision/                  # EAR, MAR, head pose, movement, facade
├── scoring/
│   ├── base.py               # Decorator pattern - Component + Decorator
│   ├── config.py              # כל הספים במקום אחד
│   ├── evaluator_factory.py   # מרכיבה את שרשרת ה-decorators
│   ├── score_engine.py        # מרדף יעד + rolling average + התאוששות
│   └── decorators/             # 4 עונשים קונקרטיים
├── networking/               # API client מאובטח + DTOs
├── session_logging/          # DataLogger (CSV) - היה חסר במקור!
└── ui/                       # ציור overlay + טיפול מקלדת

server/
├── main.py                   # הרצת uvicorn
├── app.py                    # App Factory - חיווט הכל
├── config.py                  # הגדרות מ-.env (Pydantic Settings)
├── api/v1/                    # ראוטרים דקים (scores, dashboard)
├── core/                       # security, rate limiting, security headers, exceptions
├── domain/                     # Pydantic schemas + validation
├── db/                          # SQLAlchemy models + session
├── repositories/                # In-memory cache + Decorator להתמדה ב-DB
├── services/                    # לוגיקה עסקית
├── templates/dashboard.html     # דשבורד חי (HTML/JS, מתעדכן כל שנייה)
└── scripts/generate_password_hash.py
```
