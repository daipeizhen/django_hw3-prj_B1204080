"""Django 專案的主要設定檔 (settings)。

此檔案負責定義：
1. 專案路徑與安全性相關設定（BASE_DIR、SECRET_KEY、DEBUG、ALLOWED_HOSTS）
2. 安裝的應用程式 INSTALLED_APPS
3. 中介軟體 MIDDLEWARE
4. URL 入口 ROOT_URLCONF 與 WSGI/ASGI 應用程式
5. 資料庫、國際化、靜態檔案等設定
"""

from pathlib import Path  # 處理檔案與目錄路徑的標準庫
import os  # 若日後需要使用環境變數，可透過 os 模組
import tempfile

# 專案根目錄，例如 .../django_bmi-mgt
BASE_DIR = Path(__file__).resolve().parent.parent

# Django 用來簽署 cookies 等安全用途的金鑰（正式環境請改為環境變數）
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-food-tracker-demo-secret-key')

# 除錯模式：開發時設為 True，正式上線務必改為 False
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# 允許存取此站台的主機名稱或 IP，'*' 代表所有來源皆可（僅適合教學/開發）
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')


# ------------------------------
# 應用程式註冊區 (INSTALLED_APPS)
# ------------------------------
INSTALLED_APPS = [
    # Django 內建管理後台
    'django.contrib.admin',
    # 使用者與權限系統
    'django.contrib.auth',
    # 內容型別框架（權限等功能會用到）
    'django.contrib.contenttypes',
    # 工作階段 (session) 支援
    'django.contrib.sessions',
    # 訊息框架（可顯示一次性提示訊息）
    'django.contrib.messages',
    # 靜態檔案 (CSS、JS、圖片) 管理
    'django.contrib.staticfiles',
    # 第三方：Django REST framework，用於建立 API
    'rest_framework',
    # 本專案的飲食記錄應用
    'food_tracker',
]


# ------------------------------
# 中介軟體設定 (MIDDLEWARE)
# ------------------------------
MIDDLEWARE = [
    # 安全性相關的中介軟體（如安全 header 等）
    'django.middleware.security.SecurityMiddleware',
    # Session 支援
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 一般 HTTP 功能（如 URL 正規化等）
    'django.middleware.common.CommonMiddleware',
    # CSRF 防護
    'django.middleware.csrf.CsrfViewMiddleware',
    # 驗證目前請求的使用者
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 訊息框架支援
    'django.contrib.messages.middleware.MessageMiddleware',
    # 防止 iframe 點擊劫持
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# 專案層級 URL 入口模組（對應到 config/urls.py）
ROOT_URLCONF = 'config.urls'


# ------------------------------
# 模板 (Templates) 設定
# ------------------------------
TEMPLATES = [
    {
        # 使用 Django 內建的模板引擎
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 額外尋找模板的路徑：本專案主要使用 app/templates
        'DIRS': [],
        # 是否自動搜尋各 app 裡的 templates/ 目錄
        'APP_DIRS': True,
        'OPTIONS': {
            # 在模板中可使用的「內容處理器」（會注入一些常用變數）
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# WSGI / ASGI 應用程式路徑設定（提供給部署伺服器使用）
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# ------------------------------
# 資料庫設定 (Database)
# ------------------------------
if os.environ.get('DB_ENGINE', 'mysql') == 'sqlite':
    sqlite_dir = Path(
        os.environ.get(
            'SQLITE_DIR',
            Path(tempfile.gettempdir()) / 'django_hw3-prj_B1204080',
        )
    )
    sqlite_dir.mkdir(parents=True, exist_ok=True)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.environ.get('SQLITE_NAME', sqlite_dir / 'db.sqlite3'),
        }
    }
else:
    import pymysql

    pymysql.install_as_MySQLdb()

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': os.environ.get('MYSQL_HOST', '127.0.0.1'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'NAME': os.environ.get('MYSQL_DATABASE', 'food_tracker'),
            'USER': os.environ.get('MYSQL_USER', 'food_user'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'food_password'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }


# ------------------------------
# 國際化與時區設定 (i18n / l10n)
# ------------------------------
# 語系使用繁體中文（台灣地區常用標記 zh-hant）
LANGUAGE_CODE = 'zh-hant'

# 時區設定為台北時間
TIME_ZONE = 'Asia/Taipei'

# 啟用 Django 的翻譯與本地化機制
USE_I18N = True

# 啟用時區感知 (timezone-aware) datetime 物件
USE_TZ = True


# ------------------------------
# 靜態檔案設定 (CSS / JS / 圖片)
# ------------------------------
# 在模板中使用 {% static %} 時的 URL 前綴
STATIC_URL = 'static/'

# collectstatic 收集出來的靜態檔案實際儲存目錄
STATIC_ROOT = BASE_DIR / 'staticfiles'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}


# 預設使用 BigAutoField 作為主鍵型別，避免自動主鍵警告
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ------------------------------
# 身份認證設定 (Authentication)
# ------------------------------
# 使用者未登入時要重導向的 URL
LOGIN_URL = 'food_tracker:login'

# 使用者登入後要重導向的 URL（預設為 /accounts/profile/，這裡改為首頁）
LOGIN_REDIRECT_URL = 'food_tracker:home'

# 使用者登出後要重導向的 URL
LOGOUT_REDIRECT_URL = 'food_tracker:home'
