# settings.py MÍNIMO para PythonAnywhere - SOLO APPS BÁSICAS
# Copia TODO este contenido y reemplaza completamente tu settings.py

import os

BASE_DIR = '/home/Dalej/multi'

SECRET_KEY = 'django-insecure-your-secret-key-here'

DEBUG = True

ALLOWED_HOSTS = ['dalej.pythonanywhere.com', 'localhost', '127.0.0.1']

# Application definition - SOLO APPS BÁSICAS que no dependen de usuarios
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'productos',    # Esta app debería funcionar sola
    'chatbot',      # Esta app debería funcionar sola
    # 'usuarios',   # Comentado - causa conflictos
    # 'pedidos',    # Comentado - puede depender de usuarios
    # 'recibos',    # Comentado - depende de usuarios (Cliente)
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

# Login usando el modelo User de Django por defecto
LOGIN_URL = 'admin:login'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 86400

APPEND_SLASH = True

CSRF_TRUSTED_ORIGINS = ['https://dalej.pythonanywhere.com']

print("✅ Settings MÍNIMO configurado correctamente para PythonAnywhere")
