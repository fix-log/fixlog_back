import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(APP_DIR.parent / ".env.local")  # env 파일 설정

from .base import *

DEBUG = True
ENVIRONMENT = "local"
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
REST_FRAMEWORK["EXCEPTION_HANDLER"] = "rest_framework.views.exception_handler"
