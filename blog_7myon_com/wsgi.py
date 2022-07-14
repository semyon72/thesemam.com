"""
WSGI config for blog_7myon_com project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os, sys
from pathlib import Path

APP_ROOT_PATH = str(Path(__file__).resolve().parent.parent)
# APP_DEBUG_START_MESSAGE = "APP-DBG"

# print(APP_DEBUG_START_MESSAGE, APP_ROOT_PATH, file=sys.stderr)
# print(APP_DEBUG_START_MESSAGE, 'SYS.PATH ORIG:', sys.path, file=sys.stderr)
sys.path.insert(0, APP_ROOT_PATH)
# print(APP_DEBUG_START_MESSAGE, 'SYS.PATH NEW:', sys.path, file=sys.stderr)



from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_7myon_com.settings')

application = get_wsgi_application()
