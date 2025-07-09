import os
from pathlib import Path

from dotenv import load_dotenv

from .base import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env.prod")  # env 환경 분리 설정

DEBUG = False
ENVIRONMENT = "production"
