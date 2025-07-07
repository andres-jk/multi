# 🔧 SOLUCIÓN INMEDIATA - PROBLEMA CON __file__

## El problema que tienes es que cuando copias el código, los guiones bajos se pierden

### ❌ PROBLEMA:
```python
BASE_DIR = Path(file).resolve().parent.parent  # ← INCORRECTO
```

### ✅ SOLUCIÓN:
```python
BASE_DIR = Path(__file__).resolve().parent.parent  # ← CORRECTO (con doble guión bajo)
```

## 🚀 COMANDOS INMEDIATOS para PythonAnywhere:

### 1. Borrar y reemplazar settings.py:
```bash
cd /home/Dalej/multi
rm multiandamios/settings.py
nano multiandamios/settings.py
```

### 2. Copia EXACTAMENTE este contenido (asegúrate de que __file__ tenga doble guión bajo):
```python
import os

BASE_DIR = '/home/Dalej/multi'

SECRET_KEY = 'django-insecure-your-secret-key-here'

DEBUG = True

ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'productos',
    'pedidos',
    'recibos',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'multiandamios.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/home/Dalej/multi/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'multiandamios.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/Dalej/multi/db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = '/home/Dalej/multi/staticfiles'
STATICFILES_DIRS = ['/home/Dalej/multi/static']

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/Dalej/multi/media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 86400

APPEND_SLASH = True

CSRF_TRUSTED_ORIGINS = ['https://dalej.pythonanywhere.com']
```

### 3. Guardar archivo en nano:
- Ctrl+O (guardar)
- Enter (confirmar nombre)
- Ctrl+X (salir)

### 4. Probar que funciona:
```bash
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Reload en PythonAnywhere:
Ve a la pestaña "Web" y haz clic en "Reload dalej.pythonanywhere.com"

## 🎯 IMPORTANTE:
- NO uses Path(__file__) en PythonAnywhere, usa rutas absolutas
- BASE_DIR = '/home/Dalej/multi' es más confiable
- Asegúrate de que todos los paths empiecen con '/home/Dalej/multi/'
